#### 基本环境
运行环境：类Unix环境（在Mac OS X 10.9.5、Ubuntu 13.10下运行通过）。Windows下所需的python库安装麻烦，而且需要另外的链接库访问Windows API暂未运行成功。  

首先确保有python运行环境，另外还需要有pip(方便其他python第三方库下载)以及相关的开发库(提供lxml、pyOpenssl的编译环境)。  

    sudo apt-get install python-pip  
    sudo apt-get install python-dev  
    sudo apt-get install lxml-dev

#### virtualenv
最好安装virtualenv，这样安装的第三方库都会集中在一个新的文件夹下而不是安装到系统中，能提供一个比较纯净的运行环境。可以通过`pip install virtualenv`安装，安装后进入目录，创建虚拟环境：

    virtualenv --no-site-packages  ENV  
    source ENV/bin/activate  
    
如果想退出virtualenv环境，执行
    
    deactive
    
#### Scrapy框架
这个爬虫基于Scrapy框架，因此需要安装Scrapy库：

    pip install scrapy  
    
理论上来说执行 `pip install scrapy`, 这些库都会自动被安装. 但是中途可能因为网络访问异常或者其他原因, 需要手动安装以下依赖库 (Twisted, w3lib, queuelib, lxml, pyOpenSSL, cssselect, six)

#### redis访问
分布式是通过redis数据库提供一个公共访问的队列，因此python代码中需要操作redis数据库需要相关的第三方库：

    pip install redis

#### redis服务器
需要一台机器作为主机，提供redis数据库的访问。  
Mac OS上可以
    
    brew install redis

Ubuntu上可以

    sudo apt-get install redis-server

若想通过php图形化管理redis数据库，可以安装phpRedisAdmin。详情可查看 [安装Redis图形化界面](http://jaysonhwang.sinaapp.com/blog/35) 。

#### 配置redis服务器参数
修改`settings.py`中的`REDIS_HOST`为主机所在的IP地址，然后部署到分机上。
