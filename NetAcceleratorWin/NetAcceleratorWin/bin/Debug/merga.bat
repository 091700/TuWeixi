@echo off
chcp 65001
set "ILMergePath=ILMerge.exe"  :: 如果ILMerge不在环境变量，写全路径如：C:\ILMerge\ILMerge.exe
set "MainExe=C:\Users\10200\Desktop\NetAcceleratorWin\NetAcceleratorWin\bin\Debug\NetAcceleratorWin.exe"  :: 替换为你的主程序EXE名
set "OutputExe=C:\Users\10200\Desktop\NetAcceleratorWin\NetAcceleratorWin\bin\Debug\NetAccelerator_Merged.exe"
set "TargetPlatform=v4.8,C:\Windows\Microsoft.NET\Framework64\v4.0.30319"

:: 执行合并（如果有多个DLL，在MainExe后追加，用空格分隔）
%ILMergePath% /out:%OutputExe% %MainExe% /target:winexe /targetplatform:%TargetPlatform% /wildcards

echo 合并完成（若报错请检查路径）
pause