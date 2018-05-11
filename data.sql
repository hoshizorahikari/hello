INSERT INTO roles VALUES(1,'User',1,3);
INSERT INTO roles VALUES(2,'Moderator',0,15);
INSERT INTO roles VALUES(3,'Admin',0,31);

INSERT INTO users VALUES(1,'2091248018@qq.com','hikari','pbkdf2:sha256:50000$YrSU2YIq$6d8ab7cb380dd130991753745316079bb5268826df78b742e32dd63aadbf7a41',3,1,'hikari','南京','Admin大人','2018-05-11 02:49:31.924783','2018-05-11 05:23:43.286322','/static/maki.png');
INSERT INTO users VALUES(2,'208343741@qq.com','hikari星','pbkdf2:sha256:50000$VbVCUXxe$65fdc8936125955518d90dcfcca6eb2a3e0b730c118905c8bb7ae5534399dbd6',1,1,'','','','2018-05-11 02:58:28.908664','2018-05-11 03:17:14.817036','/static/1411.png');
INSERT INTO users VALUES(3,'hikari_python@sina.com','test','pbkdf2:sha256:50000$9Q9RZ6C8$053515e2966037e8b87a02046f056cd13c526b8655f91a4844bb147e0d8a3241',1,1,NULL,NULL,NULL,'2018-05-11 02:58:50.857764','2018-05-11 03:38:16.838779','https://www.gravatar.com/avatar/0b3dcd2f549b86f7d0cae94e7927a9cd?s=256&d=monsterid&r=g');
INSERT INTO users VALUES(4,'hikari_python@163.com','python','pbkdf2:sha256:50000$eLxuCIDS$3f9245f0f1ed8ef4fdb0191b914e9fa19e1e4ef87d4cb21bab13fd0c0d896eef',1,1,'不知道','火星','跳出三界外，不在五行中。','2018-05-11 02:59:18.379661','2018-05-11 03:03:50.111827','https://www.gravatar.com/avatar/50cec57967393664875cce9916a196ac?s=256&d=monsterid&r=g');


COMMIT;
