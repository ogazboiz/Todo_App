app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:ogazboiz@localhost:5432/todoapp'

<html>
  <head>
    <title>Todo App</title>
  </head>
  <body>
    <ul>
      {% for d in data %}
      <li>{{ d.description }}</li>
      {% endfor %}
    </ul>
  </body>
</html>