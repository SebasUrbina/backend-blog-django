# Notes

Hola. Estuvo bastante entrete trabjaar un rato en este proyecto. Aprendí Django en la U, hace muuchos años y desconocía la existencia de Ninja. Ahí con mi amigo gepeto aprendí un poco de django-ninja y las principales diferencias de FastAPI (que es lo que mas conozco). Se que probablemente hay muchas cosas que me faltan por entender mas en profunidad de django, pero dejo acá mis resultados y en lo que trabajé un par de horas. Principalmente me enfoqué en rendimiento, analizando cada endpoint y algunas que considero buenas prácticas (Docker, precommit, etc.).


# Cosas que Hice

# Dockerización

Considero que un proyecto backend debería poder ejecutarse de forma reproducible en cualquier entorno sin depender de la configuración local del desarrollador. Además, un Dockerfile es un requisito prácticamente obligatorio para cualquier despliegue moderno, mientras que docker-compose facilita el desarrollo local al levantar todos los servicios necesarios de forma aislada.


# Mejoras de rendimiento

## Paginación

El endpoint que lista los posts devolvía todos los registros sin ningún mecanismo de paginación.

Esto funciona para pocos datos, pero no escala cuando el volumen crece. Se incorporó paginación para limitar la cantidad de resultados por petición, reducir el consumo de memoria y mejorar los tiempos de respuesta. 

## Optimización de consultas

Durante la revisión encontré algunos endpoints donde se realizaban múltiples consultas que podían resolverse de forma más eficiente. 

> Conversación ChatGPT de referencia: https://chatgpt.com/share/6a5969fc-f8e4-83e9-9f83-5181deb728d8

En particular, con ayuda de mi amigo gepeto, aproveché select_related, prefetch_related y anotaciones (annotate) cuando correspondía para disminuir la cantidad de consultas a la base de datos y evitar problemas del tipo N+1 Query.

El objetivo fue que la mayor parte del trabajo fuese realizado por la base de datos mediante joins y agregaciones, en lugar de resolverlo desde Python. Igual, el caso de buscar un user dado un id, en su momento pensé dejarlo como una única query pero me percaté de que era ineficiente dado que si hay mucha volumetría de posts y comentarios calcular el conteo por usuario requería una query bastante lenta. Para ese caso lo dejé como estbaa.

### Actualización del contador de visualizaciones

El incremento del contador de vistas realizaba un save() completo sobre el modelo.

Esto presenta dos problemas:

- Puede modificar accidentalmente campos como updated_at (cuando utilizan auto_now=True), perdiendo el significado de "última modificación real".
- Existe riesgo de condiciones de carrera cuando múltiples usuarios consultan el mismo post simultáneamente.

La solución fue utilizar actualizaciones atómicas mediante expresiones F() y actualizar únicamente el campo correspondiente. Esté análisis lo conseguí con la ayuda de mi amigo gepeto.

## Serialización

Mi intuición me decia que serializar los objetos en la API era redundante, como pasa en FastAPI ya que el framework nos regala eso, en este caso Ninja tiene esa capacidad. Lo que evidentemente agrega boilerplate al código. Simplifiqué el flujo utilizando directamente los Schema de Ninja.


Si updated_at tiene auto_now=True (muy común), este save() sin update_fields va a pisar updated_at cada vez que alguien lee el post. Vas a perder la semántica de "última edición real" — un post que nadie tocó hace meses va a aparecer como "actualizado ahora" solo porque alguien lo miró. Fix mínimo:

Race condition en el contador

En general existía una mala optimización de las queries, por consulta. Por ejemplo en get_post se estaban haciendo varias queries en paralelo. Para ello descubrí que con anootations en Ninja se puede optimizar todo con joins internamente. 

## Indices

Dado la naturaleza de la aplicación y el uso de algunos endpoint para obtener información ordenada por timestamp y con un criterio booleanos es que una manera de mejorar el rendimiento requiere crear un indice que involucre esos atributos para hacer más rápida la búsqueda. Para ello incorporé dos indices en la tabla de Post.


# Transversal

## Pre-commit. 

Agregué configuración de pre-commit.

Esta herramienta ayuda a mantener un estándar consistente de calidad de código, independiente del desarrollador que realice cambios.

Idealmente estos mismos checks deberían ejecutarse también dentro del pipeline de CI/CD para garantizar que todo cambio cumpla automáticamente las reglas definidas.

## Documentación de la API

Se documentaron los esquemas de entrada y salida.

Agregué documentación tanto en los schemas de entrada como salida. Al utilizar Django Ninja, esta información se refleja automáticamente en Swagger/OpenAPI, haciendo que la API sea más sencilla de consumir y mantener. 

## Estructura del proyecto.

Por un momento pensé en modularizarla más pero dado que es una app relativamente sencilla di pie atrás.

## Locust

Hace un tiempo atrás descubrí locust, una herramienta para hacer pruebas de carga. Con ayuda de la IA construí un archivo locust/locustfile.py el cual puede permitir simular cargas de trabajo de la API. La verdad se notó mucho el cambio con las mejoras de rendimiento en los endpoint pasando de segundos a ms. 

## Helm Chart

Igual, dado que he trabajado ultimamente con kubernetes, si quisiesemos desplegar este servicio en un cluster, cree (con ayuda de la IA) un helm chart que permite desplegar el servicio en un cluster y varias configuraciones. Por qué lo hice? porque puedo y se que puede ser útil dependiendo del contexto. Se puede ir iterando dependiendo de la infra.

# Cosas que no hice

## Reestructuración completa del proyecto

Consideré reorganizar la estructura del proyecto (por ejemplo, separar routers, schemas y lógica de negocio en módulos más pequeños).

Sin embargo, el tamaño actual del proyecto aún no justifica esa complejidad adicional. Preferí mantener una estructura simple y consistente antes que introducir abstracciones prematuras.

## Optimizaciones prematuras

No incorporé mecanismos de caché, las cuales pueden impactar notablemente el rendimiento, como por ejemplo; el uso de redis.

Actualmente el proyecto no presenta evidencia de necesitar ese nivel de complejidad y preferí enfocarme primero en resolver los problemas de rendimiento más evidentes en los endpoints.

## Cambios funcionales

Intenté mantener el comportamiento de la aplicación intacto.

El foco estuvo en mejorar mantenibilidad, rendimiento y calidad del código sin modificar la funcionalidad esperada.

# Qué haría si tuviera otro día?

En general me entró las ganas de llevar esto a producción, por lo lo mas probable, independientemente de la postulación iré perfeccionando esta aplicación, asi me sirve para tener un blog e2e y aprender más de django-ninja :D.

Sin embargo, si tuviese más tiempo. Haría lo siguiente;

- Integrarme con GH Actions, con el precommit y asegurar la mantención del código.
- Incorporar métricas de rendimiento, a través de Prometheus.
- Agregar mas tests si lo amerita el crecimiento de la app.
