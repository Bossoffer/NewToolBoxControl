# NewToolBoxControl
Used to disable Os-Easy computer lab controls, allowing you to enjoy using the computers without restrictions.

![ToolBox_logo](https://github.com/user-attachments/assets/60781085-9ef1-4b60-afa1-a36903f9fe07)

------------------------------------------------------------------------------------------------------
> [!IMPORTANT]
>  1. **ToolBox.exe文件需要以管理员权限运行!**   
>  2. 适用于所有桌面云环境的Os-Easy学生端
>  3. 系统版本最低需Win10，如果为Win7需等待开发者构建适用于Win7版本!

## 🚀 快速开始

> [!IMPORTANT]
>  1. 遇到脚本提示拒绝访问则需要**停止学生端根服务**
>  2. 遇到脚本不能成功运行需要管理员运行或者通过脚本运行


3.如果你发现学生端没有自动重启可以手动重启服务

1. **解除学生端自带的键鼠锁定 断网锁定 远程控制**

   `其他管理 -> 删除键盘锁驱动&控屏锁定程序&黑屏安静 -> 三者一起删除`      
   等待删除完毕后 可以按任意按键跳过注销脚本的等待    
   待注销完毕后回到登录回来继续步骤
   * 有人说学生端不再会自启动 如果要恢复学生端    
   长按 `进程管理 -> 开关学生端根服务`    
   如果机器太卡可自己开 cmd 运行 `sc start mmpc`    
     

2. **解锁网络限制**    

   `其他管理 -> 解除网络限制锁`     
   或者 `DLL工具 -> 执行:关闭网络管控`
   如果老师平时不锁网络可以跳过这一步     
   如果不需要广播管理等功能可以直接跳过下面的步骤     
   直接 `进程管理 -> 挂起学生端主进程` 挂起进程后直接开玩 (
      

3. **配置外置屏幕广播**
   
   点击任务栏处的学生端 在弹出的菜单中点击设置 查看其教师机IP地址    
   `广播命令 -> 输入教师机IP` 把看到的IP抄进去     
   随后按 `由教师机IP生成广播命令`     
   接着打开`广播管理`的快捷键相关选项

   **可能会出现的问题**    
   工具箱获取到的本机IP地址不正确    
   你需要使用`读取已拦截的广播命令`自行修改其`#local#`的值为本机IP    
   接着粘贴到上一个输入框中 随后 `手动更新广播命令`


✨ 机房实战效果截图
<details>
<summary>点击展开查看截图</summary>



</details>

--------------------------------------------------------------------------------------------------------

### 👀 工具箱界面截图   
<details>
<summary>点击展开查看截图</summary>
<img width="436" height="628" alt="1" src="https://github.com/user-attachments/assets/5a75566e-f15a-463a-afed-f742386d6d5f" />

<img width="436" height="628" alt="2" src="https://github.com/user-attachments/assets/601f9222-e940-40f6-9b7a-40d6d2203ed3" />

<img width="436" height="628" alt="3" src="https://github.com/user-attachments/assets/49f070ea-798a-44f2-bb3a-8b5bdee463d8" />

<img width="436" height="628" alt="5" src="https://github.com/user-attachments/assets/a0dcefb6-2dfc-498b-a82a-34c4168dd04b" />

<img width="1350" height="513" alt="4" src="https://github.com/user-attachments/assets/6342ed71-9303-4b99-bd3d-6b74e8e2f178" />


</details>

--------------------------------------------------------------------------------------------------------


### 最后感谢@ZiHaoSaMa66 作者提供帮助
<img width="137" height="54" alt="图片" src="https://github.com/user-attachments/assets/a0ca0857-ae0a-4344-ab49-b8ddd6f1d55f" />

如果你喜欢我的小工具箱可以点个⭐Star⭐   
感谢有你们的Star鼓励和支持💖     
有问题&发现Bug&提供建议可以提提issue，我看到都会回哦！

## 免责声明

本项目仅供**教育研究**和**技术学习**目的，旨在学习研究软件运行机制和原理而生，禁止用于任何非法用途。   
本软件包含可能影响系统稳定的实验性代码，操作不当可能导致：    
系统数据丢失或损坏、应用程序异常崩溃等，使用者需自行承担所有操作风险，使用前应做好完整系统备份。
 
开发者/贡献者不对以下情况负责：
- 因使用本项目造成的直接/间接损失
- 违反用户所在机构相关规定导致的后果
- 因软件使用导致的任何法律纠纷

**继续使用即表示您已充分阅读、理解并同意承担所有相关风险及法律责任**
