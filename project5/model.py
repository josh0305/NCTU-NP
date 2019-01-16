from peewee import *
hostname = "your hostname"
username = "your username"
password = "your password"
db = MySQLDatabase('database name', host = hostname, port = 3306, user = username, passwd = password)


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    username = CharField(unique=True)
    password = CharField()


class Invitation(BaseModel):
    inviter = ForeignKeyField(User, on_delete='CASCADE', related_name = 'inviter')
    invitee = ForeignKeyField(User, on_delete='CASCADE', related_name = 'invitee')


class Friend(BaseModel):
    user = ForeignKeyField(User, on_delete='CASCADE', related_name = 'user')
    friend = ForeignKeyField(User, on_delete='CASCADE', related_name = 'friend')


class Post(BaseModel):
    user = ForeignKeyField(User, on_delete='CASCADE')
    message = CharField()


class Token(BaseModel):
    token = CharField(unique=True)
    owner = ForeignKeyField(User, on_delete='CASCADE')
    channel = CharField(unique=True)


class Group(BaseModel):
    name = CharField(unique=True)
    channel = CharField(unique=True)


class GroupMember(BaseModel):
    group = ForeignKeyField(Group, on_delete='CASCADE',  related_name = 'group')
    member = ForeignKeyField(User, on_delete='CASCADE',  related_name = 'member')


if __name__ == '__main__':
    db.connect()
    db.create_tables([User, Invitation, Friend, Post, Token, Group, GroupMember])
