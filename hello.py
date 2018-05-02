from flask import Flask
from flask import request
from flask_script import Manager
app = Flask(__name__)
manager=Manager(app)

#----------------
dct = {5: 'rin', 6: 'maki', 7: 'nozomi'}

# @app.route('/')
# def index():
#     user_agent = request.headers.get('User-Agent')
#     return '<h1 style=color:red>hello world!</h1><br><p>{}</p>'.format(user_agent)


@app.route('/user/<name>')  # 动态路由
def user(name):
    return '<h1>hello, {}!</h1>'.format(name)


from flask import abort


@app.route('/user/<int:id>')
def user1(id):
    name = dct.get(id)
    if name is None:
        abort(404)
    return '<h1>hello, {}!</h1>'.format(name)


if __name__ == '__main__':
    # 默认端口5000, 可以修改
    # app.run(debug=True, port=8000)
    manager.run()
