sudo apt-get install python-pip  
sudo apt-get install python-dev  
sudo apt-get install lxml-dev
pip install virtualenv  
virtualenv --no-site-packages  ENV  
cd ENV/  
source ./bin/activate  
pip install scrapy  
理论上来说执行 `pip install scrapy`, 这些库都会自动被安装. 但是中途可能因为网络访问异常或者其他原因, 需要手动安装以下依赖库 (Twisted, w3lib, queuelib, lxml, pyOpenSSL, cssselect, six)

	lpush webmodel:urls_to_visit http://www.qq.com http://www.hexun.com http://www.sohu.com http://www.people.com.cn http://xinhuanet.com http://163.com http://www.cntv.com http://www.ifeng.com http://www.sina.com.cn 
	
pip install redis

from pybloom import BloomFilter as BF
from pprint import pprint as pp
