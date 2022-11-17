from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sys

app = Flask(__name__)
app.app_context().push()


# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:ogazboiz@localhost:5432/todoapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class TodoList(db.Model):
    __tablename__ = 'todolists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    todos = db.relationship('Todo', backref='list', lazy=True)
    completed = db.Column(db.Boolean, default = False)

class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    completed = db.Column(db.Boolean, default = False)
    list_id = db.Column(db.Integer, db.ForeignKey('todolists.id'), nullable=False)

@app.route('/')
def index():
    return redirect(url_for('get_list_todos', list_id=1))

@app.route('/lists/<list_id>')
def get_list_todos(list_id):
    
    todo_list = Todo.query.filter_by(list_id=list_id).order_by('id').all()
    return render_template('index.html',lists = TodoList.query.all(),active_list=TodoList.query.get(list_id), todo_list=todo_list)

@app.route("/todos/create", methods=['POST'])
def create_todo():
    #create new item
    error = False
    try:
        body={}
        title = request.get_json()['title']
        list_id = request.get_json()['list_id']
        new_todo = Todo(title=title, completed=False, list_id=list_id)
        db.session.add(new_todo)
        db.session.commit()
        body['title'] = new_todo.title
        body['id'] = new_todo.id
        body['completed'] = new_todo.completed
        
        
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if  error == True:
            abort(400)
        else:            
            return jsonify(body)
@app.route('/todos/<todo_id>/set-completed', methods=['POST'])
def set_completed_todo(todo_id):
    #updating new item
    try:
        completed = request.get_json()['completed']
        todo = Todo.query.get(todo_id)
        todo.completed  = completed
        db.session.commit() 
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for("index"))

# @app.route("/update/<int:todo_id>")
# def update(todo_id):
#     #add new item
#     todo = Todo.query.filter_by(id=todo_id).first()
#     todo.complete = not todo.complete
#     db.session.commit()
#     return redirect(url_for("index"))

# @app.route("/delete/<int:todo_id>")
# def delete(todo_id):
#     #delete item
#     todo = Todo.query.filter_by(id=todo_id).first()
#     db.session.delete(todo)
#     db.session.commit()
#     return redirect(url_for("index"))
@app.route('/todos/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
  try:
    todo = Todo.query.filter_by(id=todo_id).first()
    db.session.delete(todo)
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return jsonify({ 'success': True })

@app.route('/lists/create', methods=['POST'])
def create_list():
    error = False
    body = {}
    try:
        name = request.get_json()['name']
        todolist = TodoList(name=name)
        db.session.add(todolist)
        db.session.commit()
        body['id'] = todolist.id
        body['name'] = todolist.name
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info)
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return jsonify(body)

@app.route('/lists/<list_id>/delete', methods=['DELETE'])
def delete_list(list_id):
    error = False
    try:
        list = TodoList.query.get(list_id)
        for todo in list.todos:
            db.session.delete(todo)

        db.session.delete(list)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return jsonify({'success': True})


@app.route('/lists/<list_id>/set-completed', methods=['POST'])
def set_completed_list(list_id):
    error = False

    try:
        list = TodoList.query.get(list_id)
        completed = request.get_json()['completed']
        for todo in list.todos:
            todo.completed = True
        list.completed = completed
        db.session.commit()
    except:
        db.session.rollback()

        error = True
    finally:
        db.session.close()

    if error:
        abort(500)
    else:
        return '', 200

if __name__ == "__main__":
    # db.create_all()
    app.run(host="0.0.0.0", debug=True)
    