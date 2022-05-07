# 光谱渲染

## 简介

顾名思义，这是个能够渲染光谱的程序。

但是他的GUI上渲染的是双缝干涉。

你可以调整滑块或者点击按钮来调整双缝干涉的参数。

最终右上角会显示光屏上的内容，而右下角则会显示从双缝到光屏俯视看到的的内容。

## 依赖

可通过

``
pip install -r requirements.txt
``

安装所需依赖。

## 打包

可通过

``
pyinstaller -F -w --i "icon.png" --add-data "icon.png;." --add-data "spectrum.png;." main.py
``

打包此项目。

## 程序结构

ui.py主要负责基于PyQt5的GUI绘制。

constants.py中基本是将光的物理参数转为sRGB(日常所用rgb值)的常数，不是很熟悉就不要动了。

colorUtils.py负责将特定波长光强的光转为sRGB值，附带了个绘制光谱的实例。

calculationUtils.py负责双缝干涉的相关计算/渲染，附带实例。

main.py为本程序入口。