from logging import warning
from flask import Flask
from flask import render_template, redirect, url_for, request,flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from datetime import datetime
import matplotlib.pyplot as plt 
from flask_restful import Resource,Api,reqparse,fields,marshal_with,abort,inputs


#API--------->

api=Api()

## list API------->

list_req=reqparse.RequestParser()    #to parse the request and convert it into a dictonary

list_req.add_argument('id',type=int,help='id is an integer')
list_req.add_argument('user_id',type=int,help='user_id is an integer')
list_req.add_argument('title',type=str,help='title is a string')
list_req.add_argument('description',type=str,help='description is a string')

#to convert the class obj into json
list_field={
    'title':fields.String,
    'description':fields.String,
    'user_id':fields.Integer,
    'id':fields.Integer
}

class ListAPI(Resource):
    @marshal_with(list_field)
    def get(self,id=None):
        user=User.query.filter_by(id=id).first()
        if user:
            list=List.query.filter_by(user_id=id).all()
            if len(list)>0:
                return list
            else:
                abort(400,message="user is in the database but does not have any task at the moment")
        else:
            abort(404,message="no user with this id")
            
        
    
    @marshal_with(list_field)
    def post(slef):
        data=list_req.parse_args()
        user_id=data.get('user_id',None)

        user=User.query.filter_by(id=user_id).first()
        if not user:
            abort(404,message="user id not in the database")
        else:

            title=data.get('title', None)
            description=data.get('description',None)

            list=List.query.filter_by(user_id=user_id).all()
            
            new_list=List(description=description,title=title,user_id=user_id)
            db.session.add(new_list)
            db.session.commit()
            return new_list , 201


    @marshal_with(list_field)
    def put(self):
        data=list_req.parse_args()
        user_id=data.get('user_id',None)
        
        user=User.query.filter_by(id=user_id).first()
        if not user:
            abort(404,message="user id not in the database")
        else:
            list_id=data.get('id',None)

            list=List.query.filter_by(user_id=user_id,id=list_id).first()
            
            if (list):
                list.title=data.get('title',None)
                list.description=data.get('description',None)
                db.session.commit()
                return list,201
            else:
                abort(400,message="user does not have any list with this list_id try updating other tasks")

        
            
            
    def delete(self,id=None,lid=None):
            user=User.query.filter_by(id=id).first()
            if not user:
                abort(404,message="no user with this id ")
            else:
                list=List.query.filter_by(user_id=id,id=lid).first()
                if list:
                    db.session.delete(list)
                    db.session.commit()
                    return 'list deleted',200
                else:
                    abort(404,message="user does not have any list with this list_id try deleting other tasks")


api.add_resource(ListAPI , '/api/lists','/api/lists/<int:id>','/api/lists/<int:id>/<int:lid>')


## card API----------->

card_req=reqparse.RequestParser()

card_req.add_argument('id',type=int,help='id is an integer')
card_req.add_argument('content',type=str,help='content is  a string')
card_req.add_argument('deadline',type=inputs.datetime_from_rfc822,help='deadline is a datetime')
card_req.add_argument('is_completed',type=bool,help='is_completed is a boolean')
card_req.add_argument('user_id',type=int,help='user_id is an integer')
card_req.add_argument('list_id',type=int,help='list_id is an integer')


card_field={
    'id':fields.Integer,
    'content':fields.String,
    'deadline':fields.DateTime,
    'is_completed':fields.Boolean,
    'user_id':fields.Integer,
    'list_id':fields.Integer
}

class CardAPI(Resource):

    @marshal_with(card_field)
    def get(self,id=None):
        user=User.query.filter_by(id=id).first()
        if user:
            cards=Card.query.filter_by(user_id=id).all()
            if len(cards)>0:
                print(cards[0])
                return cards
            else:
                abort(400,message="user is in the database but does not have any card at the moment")
        else:
            abort(404,message="no user with this id")


    @marshal_with(card_field)
    def post(self):
        data=card_req.parse_args()
        user_id=data.get('user_id',None)

        user=User.query.filter_by(id=user_id).first()
        if not user:
            abort(404,message="user id not in the database")
        else:
            list_id=data.get('list_id',None)
            list=List.query.filter_by(id=list_id).all()

            if len(list)==0:
                abort(400,message='user is in the database but does not have any list where you can add a card ,add a list first')
            else:
                cards=Card.query.filter_by(list_id=list_id).all()
                if len(cards)<2:
                    deadline=data.get('deadline',None)
                    content=data.get('content',None)
                    is_completed=data.get('is_completed',None)

                    new_card=Card(deadline=deadline,content=content,is_completed=is_completed,list_id=list_id,user_id=user_id)
                    db.session.add(new_card)
                    db.session.commit() 
                    print(deadline)
                    return new_card
                else:
                    abort(403,message=' limit exceeds , atmost two cards can be added ')

    @marshal_with(card_field)
    def put(self):
        data=card_req.parse_args()
        user_id=data.get('user_id',None)
        
        user=User.query.filter_by(id=user_id).first()
        if not user:
            abort(404,message="user id not in the database")
        else:
            list_id=data.get('list_id',None)
            list=List.query.filter_by(user_id=id,id=list_id).first()
            if  not list:
                abort(404,message='user is in the database but does not have any list where you can edit a card ,add a list first')
            else:
                id=data.get('id')
                cards=Card.query.filter_by(list_id=list_id,id=id).first()
                cards.content=data.get('content')
                cards.is_completed=data.get('is_completed')
                db.session.commit()
                return cards


    def delete(self,id,lid,cid):
        user=User.query.filter_by(id=id).first()
        if not user:
            abort(404,message="no user with this id ")
        else:
            list=List.query.filter_by(user_id=id,id=lid).first()
            if list:
                card=Card.query.filter_by(user_id=id,list_id=lid,id=cid).first()
                if card:

                    db.session.delete(card)
                    db.session.commit()
                    return "card deleted",200
                else:
                    abort(404,message="no such card exist,try deleting a card with valid card_id ")

            else:
                abort(404,message="user does not have any list with this list_id")



api.add_resource(CardAPI, '/api/cards','/api/cards/<int:id>','/api/cards/<int:id>/<int:lid>/<int:cid>')




#app instances----------->

app = Flask(__name__)
api.init_app(app)      #embedding api instance to the application
db = SQLAlchemy(app)     
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///kanban_database.db'
app.secret_key='alohamora'       #client side session secure

login_manager = LoginManager()        #access control ,user session manageent
login_manager.init_app(app)
login_manager.login_view = "signin"    #url where log-in happens

@login_manager.user_loader            #current logged-in user
def load_user(user_id):
    return User.query.get(int(user_id))


#database tables------------>

class User(db.Model,UserMixin):                    #authentication , is_active, is_annanymous         
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    email= db.Column(db.String(30), nullable=False,unique=True )
    list= db.relationship('List', backref='user')
    cards=db.relationship('Card', backref='user')

class List(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.String(100), nullable=False)
    title=db.Column(db.String(20), nullable=False)
    # list_type = db.Column(db.String(40), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    cards = db.relationship('Card', backref='List', cascade='all ,delete')

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    list_id = db.Column(db.Integer, db.ForeignKey('list.id'), nullable=False)
    deadline = db.Column(db.DateTime())
    content=db.Column(db.String(100), nullable=False)
    is_completed = db.Column(db.Boolean,default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)



    
#logics and routes------------>

@app.route('/')
def home():
    return render_template('welcome.html')



@app.route('/signup')
def signup():
    return render_template('signup.html')



@app.route("/signup",methods=['POST'])
def signup_post():
    name=request.form['name']
    email=request.form['email'] 
    user=User.query.filter_by(name=name,email=email).first()
    if user:
        flash(f' already a user','warning')
        return redirect(url_for('signin'))      
    new_user=User(name=name,email=email)
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('signin'))



@app.route('/signin')
def signin():
    return render_template('signin.html')



@app.route("/signin" , methods=['POST'])
def signin_post():
    name=request.form.get('name')
    email=request.form.get('email')
    user=User.query.filter_by(name=name,email=email).first()
    if  not user:
        flash(f'couldnt find you in the database. incorrect email or new user? ','info')
        return redirect(url_for('signup'))
    login_user(user)
    return  redirect(url_for(('dashboard')))         
    



@app.route("/dashboard",methods=['POST','GET'])
@login_required
def dashboard():
    info=User.query.filter_by(id=current_user.id).first()
    tasks=List.query.filter_by(user_id=current_user.id).all()
    total_task=List.query.filter_by(user_id=current_user.id).count()
    total_cards=Card.query.filter_by(user_id=current_user.id).count()
    completed=Card.query.filter_by(user_id=current_user.id,is_completed=True).count()
    pending=Card.query.filter_by(user_id=current_user.id,is_completed=False).count()




    if request.method=='POST':
        
        description=request.form["description"]
        title=request.form['title']
        task=List(description=description,title=title,user_id=current_user.id)
        db.session.add(task)
        db.session.commit()
        
        return  redirect(url_for('dashboard'))

    return render_template('dashboard.html' ,**locals())




@app.route('/<int:tid>/delete_task')
@login_required
def delete_task(tid):
    task = List.query.filter_by(id=tid).first()
    print(task)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('dashboard'))



@app.route('/<int:tid>/edit_task', methods=["POST", "GET"])
@login_required
def edit_task(tid):
    task = List.query.filter_by(id=tid).first()
    if request.method=="POST":
        task.title = request.form["title"]
        task.description = request.form["description"]
        db.session.commit()
        return redirect(url_for('dashboard', tid=tid))

    return render_template('edit_task.html', **locals())




@app.route('/<int:tid>/add', methods=['GET', 'POST'])
@login_required
def add(tid):

    task=List.query.filter_by(id=tid).first()
    extra_info = Card.query.filter_by(list_id=task.id).order_by(desc(Card.deadline)).limit(2)
    
    present = datetime.now()
    print(present)
    crr_time = present.strftime('%Y/%m/%d %H:%M')
    print(crr_time)

    if request.method=="POST":
        tid = task.id
        user_id=task.user_id
        deadline = request.form["deadline"]
        year = deadline[0:4]
        month = deadline[5:7]
        date = deadline[8:10]    
        hour = deadline[11:13]
        min = deadline[14:]
    
        crr_time = datetime(int(year), int(month), int(date), int(hour), int(min),0,0)
        # is_completed= not is_completed
        content = request.form["content"]
        if extra_info.count()>1:
            flash(f'extending deadline is not a good habit ','warning')
            return render_template('add_task.html', task=task,extra_info=extra_info, crr_timestamp=crr_time,is_completed=False,user_id=user_id)
        else:    
            crr_card = Card(list_id=task.id, deadline=crr_time,content=content, is_completed=False,user_id=task.user_id)
            db.session.add(crr_card)
            db.session.commit()

        extra_info = Card.query.filter_by(list_id=task.id).order_by(desc(Card.deadline)).limit(2)
        crr_time = datetime.now()
        crr_time = present.strftime('%Y/%m/%d %H:%M')
        print(deadline)
        print(extra_info.count())

        return render_template('add_task.html', task=task,extra_info=extra_info, crr_timestamp=crr_time,is_completed=False,user_id=task.user_id)
    return render_template('add_task.html', task=task, extra_info=extra_info, crr_timestamp=crr_time,user_id=task.user_id)




@app.route('/<int:tid>/<int:cid>/edit',methods=['POST','GET'])
def edit_card(tid,cid):
    task=List.query.filter_by(id=tid).first()
    card=Card.query.filter_by(id=cid).first()

    if request.method=="POST":
        card.is_completed =card.is_completed
        card.content=request.form['content']
        db.session.commit()

        return redirect(url_for('add', tid=tid))

    return render_template('edit_card.html', **locals())



@app.route('/<int:tid>/<int:cid>/delete')
@login_required
def delete_card(tid ,cid):
    card= Card.query.filter_by(id=cid).first()
    db.session.delete(card)
    db.session.commit()
    return redirect(url_for('add', tid=tid))


@app.route('/<int:tid>/<int:cid>/update')
@login_required
def update_card(tid,cid):
    card= Card.query.filter_by(id=cid).first()
    card.is_completed = not card.is_completed
    db.session.commit()
    return redirect(url_for('add', tid=tid))


@app.route('/<int:id>/summary')
def summary(id):
    total_task=List.query.filter_by(user_id=id).count()
    total_cards=Card.query.filter_by(user_id=id).count()
    completed=Card.query.filter_by(user_id=id,is_completed=True).count()
    pending=Card.query.filter_by(user_id=id,is_completed=False).count()
    
    x=['total_task','total_cards','completed','pending']
    y=[total_task,total_cards,completed,pending]
    z=[completed,pending]
    l=['completed','pending']

    

    per= int((completed/total_cards)*100)
    plt.bar(x,y,color=['blue','blue','green','red'])
    plt.savefig('static/bar.png')
    plt.clf()

    plt.pie(z,labels=l,colors=['green','red'])
    plt.savefig("static/pie.png")           
    plt.clf()
    plt.close()

    # except ZeroDivisionError:
    #     plt.savefig('static/bar.png')
    #     plt.clf()
    #     plt.savefig("static/pie.png")
    #     plt.clf()


        


    return render_template('summary.html',**locals())




@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('/5000'))




if __name__=='__main__':
    db.create_all()
    app.run(debug=True )
