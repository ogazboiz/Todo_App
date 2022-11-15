from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
import sys

app = Flask(__name__)
app.app_context().push()


# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:ogazboiz@localhost:5432/todoapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    complete = db.Column(db.Boolean)



@app.route('/')
def index():
    todo_list = Todo.query.all()
    return render_template('index.html', todo_list=todo_list)

@app.route("/todos/create", methods=['POST'])
def create_todo():
    #create new item
    error = False
    try:
        body={}
        title = request.get_json()['title']
        new_todo = Todo(title=title, complete=False)
        body['title'] = new_todo.title
        db.session.add(new_todo)
        db.session.commit()
        
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

if __name__ == "__main__":
    db.create_all()
    app.run(host="0.0.0.0", debug=True)
    