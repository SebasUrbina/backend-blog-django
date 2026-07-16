import random
from locust import HttpUser, task, between, events

# Predefined fallback/default values if the database is not seeded yet or API is empty
DEFAULT_POST_IDS = [1, 2, 3, 4, 5]
DEFAULT_AUTHOR_IDS = [1, 2, 3]
DEFAULT_TAG_SLUGS = ["tech", "django", "python", "locust"]
DEFAULT_EMAILS = ["user1@example.com", "user2@example.com"]
SEARCH_QUERIES = ["django", "python", "the", "lorem", "post", "ninja", "web", "database"]


class BlogUser(HttpUser):
    # Simulates a user waiting between 0.5 and 2.0 seconds between tasks
    wait_time = between(0.5, 2.0)

    def on_start(self):
        """
        Executed when a user starts. We attempt to harvest real IDs from the API
        to make our tests realistic and not depend on hardcoded IDs.
        """
        self.post_ids = list(DEFAULT_POST_IDS)
        self.author_ids = list(DEFAULT_AUTHOR_IDS)
        self.tag_slugs = list(DEFAULT_TAG_SLUGS)
        self.emails = list(DEFAULT_EMAILS)

        try:
            # Get the first page of posts to harvest real IDs
            with self.client.get("/api/posts", catch_response=True) as response:
                if response.status_code == 200:
                    data = response.json()
                    # Expecting a paginated structure or a plain list
                    posts = data if isinstance(data, list) else data.get("items", [])

                    harvested_post_ids = []
                    harvested_author_ids = []
                    harvested_tag_slugs = []

                    for post in posts:
                        if "id" in post:
                            harvested_post_ids.append(post["id"])
                        if "author" in post and "id" in post["author"]:
                            harvested_author_ids.append(post["author"]["id"])
                        if "tags" in post:
                            for tag in post["tags"]:
                                if "slug" in tag:
                                    harvested_tag_slugs.append(tag["slug"])

                    if harvested_post_ids:
                        self.post_ids = list(set(harvested_post_ids))
                    if harvested_author_ids:
                        self.author_ids = list(set(harvested_author_ids))
                    if harvested_tag_slugs:
                        self.tag_slugs = list(set(harvested_tag_slugs))

                    # If we got author IDs, let's try to harvest some of their emails to test lookup
                    for author_id in self.author_ids[:3]:
                        with self.client.get(
                            f"/api/users/{author_id}", catch_response=True
                        ) as user_response:
                            if user_response.status_code == 200:
                                user_data = user_response.json()
                                if "email" in user_data:
                                    self.emails.append(user_data["email"])
                    self.emails = list(set(self.emails))
                else:
                    response.failure(
                        f"Failed to harvest initial posts: Status {response.status_code}"
                    )
        except Exception as e:
            # Gracefully handle exceptions during startup (e.g., connection errors) and use defaults
            print(f"Warning: Could not harvest dynamic IDs on startup ({e}). Using fallbacks.")

    @task(30)
    def list_posts(self):
        """Simulates browsing the main list of published posts."""
        self.client.get("/api/posts", name="/api/posts")

    @task(40)
    def get_post(self):
        """Simulates viewing a specific post in detail with its comments."""
        post_id = random.choice(self.post_ids)
        self.client.get(f"/api/posts/{post_id}", name="/api/posts/{id}")

    @task(10)
    def search_posts(self):
        """Simulates searching for posts with a keyword."""
        query = random.choice(SEARCH_QUERIES)
        self.client.get(f"/api/posts/search?q={query}", name="/api/posts/search")

    @task(10)
    def posts_by_tag(self):
        """Simulates browsing posts that carry a specific tag."""
        slug = random.choice(self.tag_slugs)
        self.client.get(f"/api/posts/by-tag/{slug}", name="/api/posts/by-tag/{slug}")

    @task(5)
    def get_user_profile(self):
        """Simulates viewing a user's profile with post and comment counts."""
        user_id = random.choice(self.author_ids)
        self.client.get(f"/api/users/{user_id}", name="/api/users/{id}")

    @task(2)
    def find_user_by_email(self):
        """Simulates looking up a user by email."""
        email = random.choice(self.emails)
        self.client.get(f"/api/users/find?email={email}", name="/api/users/find")

    @task(1)
    def create_post(self):
        """Simulates creating a new post (low frequency)."""
        author_id = random.choice(self.author_ids)
        tags_to_use = random.sample(self.tag_slugs, min(2, len(self.tag_slugs)))

        payload = {
            "author_id": author_id,
            "title": f"Load Test Post {random.randint(1000, 9999)}",
            "body": "This is a body generated by the Locust load testing script to measure write performance.",
            "tag_slugs": tags_to_use,
        }

        with self.client.post(
            "/api/posts", json=payload, catch_response=True, name="/api/posts (POST)"
        ) as response:
            if response.status_code == 200 or response.status_code == 201:
                # Add newly created post ID to our pool for subsequent detail views
                try:
                    data = response.json()
                    if "id" in data:
                        self.post_ids.append(data["id"])
                except Exception:
                    pass
            else:
                response.failure(f"Post creation failed: Status {response.status_code}")

    @task(2)
    def create_comment(self):
        """Simulates adding a comment to a post (moderate frequency)."""
        post_id = random.choice(self.post_ids)
        author_id = random.choice(self.author_ids)

        payload = {
            "author_id": author_id,
            "body": f"Interesting load test comment {random.randint(1000, 9999)}!",
        }

        self.client.post(
            f"/api/posts/{post_id}/comments", json=payload, name="/api/posts/{id}/comments"
        )
