from datetime import datetime
from pydantic import Field
from ninja import Schema


class AuthorOut(Schema):
    id: int = Field(
        ...,
        description="The unique identifier of the author",
        examples=[1, 2, 3],
    )
    username: str = Field(
        ...,
        description="The username of the author",
        examples=["user1", "user2"],
    )
    display_name: str = Field(
        ...,
        description="The display name of the author",
        examples=["User One", "User Two"],
    )


class TagOut(Schema):
    id: int = Field(
        ...,
        description="The unique identifier of the tag",
        examples=[1, 2, 3],
    )
    name: str = Field(
        ...,
        description="The name of the tag",
        examples=["Python", "Django"],
    )
    slug: str = Field(
        ...,
        description="The slug of the tag",
        examples=["python", "django"],
    )


class PostListOut(Schema):
    id: int = Field(
        ...,
        description="The unique identifier of the post",
        examples=[1, 2, 3],
    )
    title: str = Field(
        ..., description="The title of the post", examples=["My First Post", "My Second Post"]
    )
    author: AuthorOut = Field(
        ...,
        description="The author of the post",
        examples=[{"id": 1, "username": "user1", "display_name": "User One"}],
    )
    tags: list[TagOut] = Field(
        ...,
        description="The tags associated with the post",
        examples=[[{"id": 1, "name": "Python", "slug": "python"}]],
    )
    view_count: int = Field(
        ...,
        description="The number of times the post has been viewed",
        examples=[0, 1, 2],
    )
    created_at: datetime = Field(
        ...,
        description="The timestamp when the post was created",
        examples=["2023-01-01T00:00:00Z"],
    )


class CommentOut(Schema):
    id: int = Field(
        ...,
        description="The unique identifier of the comment",
        examples=[1, 2, 3],
    )
    author: AuthorOut = Field(
        ...,
        description="The author of the comment",
        examples=[{"id": 1, "username": "user1", "display_name": "User One"}],
    )
    body: str = Field(
        ...,
        description="The body of the comment",
        examples=["This is a great post!", "I learned a lot from this."],
    )
    created_at: datetime = Field(
        ...,
        description="The timestamp when the comment was created",
        examples=["2023-01-01T00:00:00Z"],
    )


class PostDetailOut(Schema):
    id: int = Field(
        ...,
        description="The unique identifier of the post",
        examples=[1, 2, 3],
    )
    title: str = Field(
        ..., description="The title of the post", examples=["My First Post", "My Second Post"]
    )
    body: str = Field(
        ...,
        description="The body of the post",
        examples=[
            "This is the content of my first post.",
            "This is the content of my second post.",
        ],
    )
    author: AuthorOut = Field(
        ...,
        description="The author of the post",
        examples=[{"id": 1, "username": "user1", "display_name": "User One"}],
    )
    tags: list[TagOut] = Field(
        ...,
        description="The tags associated with the post",
        examples=[[{"id": 1, "name": "Python", "slug": "python"}]],
    )
    comments: list[CommentOut] = Field(
        ...,
        description="The comments associated with the post",
        examples=[
            [
                {
                    "id": 1,
                    "author": {"id": 1, "username": "user1", "display_name": "User One"},
                    "body": "This is a great post!",
                    "created_at": "2023-01-01T00:00:00Z",
                }
            ]
        ],
    )
    view_count: int = Field(
        ...,
        description="The number of times the post has been viewed",
        examples=[0, 1, 2],
    )
    created_at: datetime = Field(
        ...,
        description="The timestamp when the post was created",
        examples=["2023-01-01T00:00:00Z"],
    )
    updated_at: datetime = Field(
        ...,
        description="The timestamp when the post was last updated",
        examples=["2023-01-01T00:00:00Z"],
    )


class UserDetailOut(Schema):
    id: int = Field(
        ...,
        description="The unique identifier of the user",
        examples=[1, 2, 3],
    )
    username: str = Field(
        ...,
        description="The username of the user",
        examples=["user1", "user2"],
    )
    display_name: str = Field(
        ...,
        description="The display name of the user",
        examples=["User One", "User Two"],
    )
    email: str = Field(
        ...,
        description="The email address of the user",
        examples=["user1@example.com", "user2@example.com"],
    )
    bio: str = Field(
        ...,
        description="The biography of the user",
        examples=["I am a software developer.", "I love to code."],
    )
    post_count: int = Field(
        ...,
        description="The number of posts created by the user",
        examples=[0, 1, 2],
    )
    comment_count: int = Field(
        ...,
        description="The number of comments made by the user",
        examples=[0, 1, 2],
    )


class PostCreateIn(Schema):
    author_id: int = Field(
        ...,
        description="The ID of the author creating the post",
        examples=[1, 2, 3],
    )
    title: str = Field(
        ...,
        description="The title of the post",
        examples=["My New Post", "Another Post"],
    )
    body: str = Field(
        ...,
        description="The body content of the post",
        examples=["This is the body of my post."],
    )
    tag_slugs: list[str] = Field(
        ...,
        description="The slugs of the tags associated with the post",
        examples=[["python"], ["django"]],
    )


class PostCreateOut(Schema):
    id: int = Field(
        ...,
        description="The unique identifier of the newly created post",
        examples=[1, 2, 3],
    )
    title: str = Field(
        ...,
        description="The title of the newly created post",
        examples=["My New Post", "Another Post"],
    )


class CommentCreateIn(Schema):
    author_id: int = Field(
        ...,
        description="The ID of the author creating the comment",
        examples=[1, 2, 3],
    )
    body: str = Field(
        ...,
        description="The body content of the comment",
        examples=["This is a great post!"],
    )


class CommentCreateOut(Schema):
    id: int = Field(
        ...,
        description="The unique identifier of the newly created comment",
        examples=[1, 2, 3],
    )
