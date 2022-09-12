import datetime

from flask import Flask
from flask import request
from flask import render_template
from flask import redirect
from flask import url_for
from crawlData import crawlData
from config import Config
from utils.mongo import Mongo
from utils.process import Process
from theme1 import theme1
from theme2 import theme2
app = Flask(__name__,template_folder = 'templates/')
config=Config()
mongo=Mongo(config)
process=Process(config,mongo)

def updatenlp(group):
    print('you are update the group-table'+config.group['name'])
    from nlp.userinfo import UserInfo
    userinfo=UserInfo(config,mongo,group)
    return userinfo.getinfo()


def updatekmeans(group):
    print('you are in update groupinfo')
    from groupinfo.kmeans import KmeansModel
    kmeans = KmeansModel(config, mongo,group)
    kmeans.run_kmeans()
def updateWord(group):
    print('you are in update group')
    from wordProcess import wordProcess
    wordProcess(group).msg_processing()
    theme1(group).runTheme()
    theme2(group).runTheme2()


@app.route('/')
def index():
    return render_template('index.html',groups=process.getgroup())

@app.route('/group')
def group():
    config.group=mongo.select_one(collection='group2id',query={'rtable':request.args['id']})
    return render_template('group.html',rank1=process.rankbyf(table=config.group['table']),name=config.group['name'])

@app.route('/net')
def net():
    config.group=mongo.select_one(collection='group2id',query={'rtable':request.args['id']})
    return render_template('net.html',rank1=process.rankbyf(table=config.group['table']),name=config.group['name'])


@app.route('/user')
def user():
    config.userid=request.args['id']
    return render_template('user.html',user=process.getuser(config.userid))

@app.route('/update')
def update():
    group=mongo.select_one(collection='group2id',query={'rtable':request.args['id']})
    config.group=group  # 可能在更新期间会出现变化
    res=updatenlp(group)
    updatekmeans(group)
    mongo.db['update_res'].replace_one({'id':group['id']},{'id':group['id'],'table':group['table'],'repeat':res[0],'insert':res[1],'update':res[2],'time':res[3]},upsert=True)
    mongo.db['group2id'].update_one({'id':group['id']},{'$set':{'update_time':datetime.datetime.now().replace(microsecond=0)}},upsert=True)
    return 'ok'
@app.route('/updateLDA')
def updateLDA():
    group=mongo.select_one(collection='group2id',query={'rtable':request.args['id']})
    config.group=group  # 可能在更新期间会出现变化
    updateWord(group)

    return 'ok'
@app.route('/LDAview')
def LDAview():
    config.group=mongo.select_one(collection='group2id',query={'rtable':request.args['id']})
    mongo.db['topics_final'].insert_one({'realname':config.group['name']})
    LDA_res = mongo.select_one(collection='update_res', query={'name': config.group['rtable']})
    return render_template('lda_pass_final'+config.group['rtable']+'.html',res=LDA_res)
@app.route('/LDA')
def LDA():
    config.group=mongo.select_one(collection='group2id',query={'rtable':request.args['id']})
    filter = {'name': config.group['rtable']}
    newvalues = {"$set": {'realname':config.group['name']}}
    mongo.db['topics_final'].update_one(filter, newvalues)
    LDA_res = mongo.select_one(collection='topics_final', query={'name': config.group['rtable']})
    return render_template('LDA.html',res=LDA_res)
@app.route('/updateres')
def updateres():
    config.group = mongo.select_one(collection='group2id', query={'table': request.args['id']})
    update_res=mongo.select_one(collection='update_res',query={'table':config.group['table']})
    return render_template('update.html',res=update_res)
@app.route('/updategroup')
def updategroup():
    crawlData().updateGroupName()
    return render_template('index.html',groups=process.getgroup())
@app.route('/test')
def test():
    return render_template('test.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)