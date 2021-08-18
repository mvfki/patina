# 绿色电子包浆生成器 Patina Generator

原理详见[Lion Yang的知乎回复](https://www.zhihu.com/question/29355920)。 此人也早已有实现过相应的web app。本repository所包含的基础功能完全照搬[他的算法](https://m13253.github.io/JPEGreen/)。

A simulator of the fact that old Android OS make the images greener due to a bug in old Google's Skia library. 

>“Patina”一词是我试图机翻“包浆”的时候找到的，逆向机翻成中文又会变成“古铜色”、“绿锈”之类的意思，意外的很有意境。于是就盲目直接用了这个名字

写这个包的主要用意还是想说看到Lion的介绍以后跃跃欲试想要练手；以及想要尝试基于Python的Web App编写。

## Web App

暂时没有部署在互联网上，要启动网页小应用的话，请先下载此包并安装在本地。
在CMD/terminal等终端运行：

```
git clone https://github.com/mvfki/patina.git
cd patina
python setup.py install
patina
```

然后复制提示的网址进浏览器即可（同Wi-Fi下的其它设备应该也可以）

## API

本Repository中的代码也被整理成了Python包，包括如下部分：
- `patina.patina`，包含：
	- 对`np.ndarray`形式的图像的绿化处理`patina.patina.patina()`
	- 对`np.ndarray`形式的图像的JPG画质压缩处理`patina.patina.jpg_comp()`
- `patina.webfig`，包含：
	- 将`np.ndarray`形式的图像转化成base64 string，可在HTML网页的`<img>`标记中的直接作为`source`显示`array_to_base64()`
	- 将上述结果的base64 string转换回`np.ndarray`形式的图像`base64_to_array()`
