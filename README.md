# HMDataAugmentation

## 仓库介绍
本仓库由南京大学软件学院LIPLAB管理，用于处理鸿蒙领域代码增强任务，制作相关语料数据使用。

## 仓库概述
本仓库由以下子目录组成，每个目录下为对应子任务：
* AndroidHelper:用于分析安卓项目代码，包括代码编译检查、项目分析、代码拆解等功能。
* ArkTSAbstractor:用于分析鸿蒙项目代码，包括代码编译检查、项目分析、代码拆解、依赖解析等功能。
* ArkTSHelper:用于自动化处理鸿蒙项目代码，提取、变异UI代码，并保存相关中间结果。
* corpusHelper:用于语料处理，主要为向模型请求脚本。
* JavaAnalyzer:用于分析具体Java文件，分析安卓函数调用。
* NJUBoxHelper:用于将结果自动化存储至NJUBox。
* webCrawler:用于爬取鸿蒙、安卓相关的网页数据及开源仓库。