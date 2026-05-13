"""
金锤子 (GenForge) - 桌面应用界面
参照 JZXZBOT 风格：多角色进度显示、代码预览、技能面板
"""
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import threading
import json


class GenForgeApp:
    """金锤子桌面应用 - 多角色协作界面"""

    # ─── 配色方案 ───────────────────────────────
    COLORS = {
        "bg":          "#1E1E2E",   # 深色背景
        "sidebar":     "#181825",   # 侧边栏
        "panel":       "#313244",   # 面板背景
        "accent":      "#CBA6F7",   # 主题紫
        "green":       "#A6E3A1",   # 成功绿
        "red":         "#F38BA8",   # 错误红
        "yellow":      "#F9E2AF",   # 警告黄
        "blue":        "#89B4FA",   # 信息蓝
        "text":        "#CDD6F4",   # 主文字
        "dim":         "#6C7086",   # 次要文字
        "user_bubble": "#45475A",   # 用户气泡
        "bot_bubble":  "#1E1E2E",   # Bot 气泡
    }

    # ─── 角色配置 ───────────────────────────────
    ROLES = {
        "Architect":    {"icon": "🏛️",  "color": "#89B4FA", "label": "建筑师"},
        "CADDeveloper": {"icon": "💻",  "color": "#A6E3A1", "label": "CAD开发"},
        "Compiler":     {"icon": "🔧",  "color": "#F9E2AF", "label": "编译器"},
        "CAD":          {"icon": "📐",  "color": "#CBA6F7", "label": "AutoCAD"},
    }

    def __init__(self, agent):
        self.agent = agent
        self.root = tk.Tk()
        self.root.title("🔨 金锤子 GenForge - CAD 语义建模")
        self.root.geometry("1100x720")
        self.root.configure(bg=self.COLORS["bg"])
        self.root.minsize(900, 600)

        self._current_role = None
        self._create_layout()
        self._show_welcome()

    # ─────────────────────────────────────────────
    # 布局构建
    # ─────────────────────────────────────────────

    def _create_layout(self):
        """三栏布局：左侧边栏 | 中间聊天区 | 右侧代码面板"""

        # 顶部标题栏
        self._create_titlebar()

        # 主内容区
        main = tk.Frame(self.root, bg=self.COLORS["bg"])
        main.pack(fill="both", expand=True, padx=0, pady=0)

        # 左侧边栏（技能+状态）
        self._create_sidebar(main)

        # 中间聊天区
        self._create_chat_panel(main)

        # 右侧代码预览
        self._create_code_panel(main)

        # 底部输入区
        self._create_input_bar()

    def _create_titlebar(self):
        bar = tk.Frame(self.root, bg=self.COLORS["sidebar"], height=44)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        tk.Label(
            bar, text="🔨 金锤子 GenForge",
            font=("Arial", 13, "bold"),
            bg=self.COLORS["sidebar"], fg=self.COLORS["accent"]
        ).pack(side="left", padx=16, pady=10)

        # 连接状态
        self.status_var = tk.StringVar(value="⚪ 未连接 AutoCAD")
        self.status_label = tk.Label(
            bar, textvariable=self.status_var,
            font=("Consolas", 9),
            bg=self.COLORS["sidebar"], fg=self.COLORS["dim"]
        )
        self.status_label.pack(side="right", padx=16)

        # 刷新按钮
        tk.Button(
            bar, text="↺ 刷新技能",
            font=("Arial", 9), relief="flat",
            bg=self.COLORS["panel"], fg=self.COLORS["text"],
            activebackground=self.COLORS["accent"],
            command=self._reload_skills, padx=8
        ).pack(side="right", padx=4)

    def _create_sidebar(self, parent):
        sidebar = tk.Frame(parent, bg=self.COLORS["sidebar"], width=180)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # 技能列表
        tk.Label(
            sidebar, text="📦 已加载技能",
            font=("Arial", 9, "bold"),
            bg=self.COLORS["sidebar"], fg=self.COLORS["dim"]
        ).pack(pady=(14, 4), padx=12, anchor="w")

        self.skill_frame = tk.Frame(sidebar, bg=self.COLORS["sidebar"])
        self.skill_frame.pack(fill="x", padx=8)
        self._refresh_skill_list()

        # 分隔线
        tk.Frame(sidebar, bg=self.COLORS["panel"], height=1).pack(
            fill="x", pady=10, padx=8)

        # 多角色进度
        tk.Label(
            sidebar, text="🔄 执行流程",
            font=("Arial", 9, "bold"),
            bg=self.COLORS["sidebar"], fg=self.COLORS["dim"]
        ).pack(pady=(0, 6), padx=12, anchor="w")

        self.role_labels = {}
        for role_id, info in self.ROLES.items():
            row = tk.Frame(sidebar, bg=self.COLORS["sidebar"])
            row.pack(fill="x", padx=10, pady=1)

            lbl = tk.Label(
                row,
                text=f"  {info['icon']} {info['label']}",
                font=("Consolas", 9),
                bg=self.COLORS["sidebar"], fg=self.COLORS["dim"],
                anchor="w"
            )
            lbl.pack(side="left", fill="x", expand=True)

            dot = tk.Label(row, text="○", font=("Arial", 8),
                           bg=self.COLORS["sidebar"], fg=self.COLORS["dim"])
            dot.pack(side="right", padx=4)

            self.role_labels[role_id] = (lbl, dot)

        # 底部清空按钮
        tk.Button(
            sidebar, text="🗑  清空对话",
            font=("Arial", 9), relief="flat",
            bg=self.COLORS["panel"], fg=self.COLORS["text"],
            command=self._clear_history, padx=8, pady=4
        ).pack(side="bottom", pady=10, padx=8, fill="x")

    def _create_chat_panel(self, parent):
        frame = tk.Frame(parent, bg=self.COLORS["bg"])
        frame.pack(side="left", fill="both", expand=True)

        self.chat_text = scrolledtext.ScrolledText(
            frame,
            font=("Consolas", 10),
            bg=self.COLORS["bg"],
            fg=self.COLORS["text"],
            insertbackground=self.COLORS["text"],
            selectbackground=self.COLORS["accent"],
            relief="flat", borderwidth=0,
            wrap=tk.WORD, padx=12, pady=8
        )
        self.chat_text.pack(fill="both", expand=True)
        self.chat_text.config(state=tk.DISABLED)

        # 颜色标签
        self.chat_text.tag_config("user",      foreground=self.COLORS["blue"],   font=("Consolas", 10, "bold"))
        self.chat_text.tag_config("architect",  foreground=self.COLORS["blue"])
        self.chat_text.tag_config("developer",  foreground=self.COLORS["green"])
        self.chat_text.tag_config("compiler",   foreground=self.COLORS["yellow"])
        self.chat_text.tag_config("cad",        foreground=self.COLORS["accent"])
        self.chat_text.tag_config("success",    foreground=self.COLORS["green"])
        self.chat_text.tag_config("error",      foreground=self.COLORS["red"])
        self.chat_text.tag_config("dim",        foreground=self.COLORS["dim"])
        self.chat_text.tag_config("bold",       font=("Consolas", 10, "bold"))

    def _create_code_panel(self, parent):
        frame = tk.Frame(parent, bg=self.COLORS["sidebar"], width=320)
        frame.pack(side="right", fill="y")
        frame.pack_propagate(False)

        # 标题行
        hdr = tk.Frame(frame, bg=self.COLORS["sidebar"])
        hdr.pack(fill="x", padx=8, pady=(10, 4))

        tk.Label(
            hdr, text="📄 生成的代码",
            font=("Arial", 9, "bold"),
            bg=self.COLORS["sidebar"], fg=self.COLORS["dim"]
        ).pack(side="left")

        tk.Button(
            hdr, text="▶ 执行",
            font=("Arial", 8), relief="flat",
            bg=self.COLORS["green"], fg="#000",
            command=self._execute_code, padx=6, pady=2
        ).pack(side="right", padx=2)

        tk.Button(
            hdr, text="📋 复制",
            font=("Arial", 8), relief="flat",
            bg=self.COLORS["panel"], fg=self.COLORS["text"],
            command=self._copy_code, padx=6, pady=2
        ).pack(side="right", padx=2)

        # 代码文本框
        self.code_text = scrolledtext.ScrolledText(
            frame,
            font=("Consolas", 8),
            bg="#11111B",
            fg="#CDD6F4",
            insertbackground="#CDD6F4",
            relief="flat", borderwidth=0,
            wrap=tk.NONE, padx=8, pady=6
        )
        self.code_text.pack(fill="both", expand=True, padx=4, pady=(0, 4))

        # 仅生成代码（不执行）按钮
        tk.Button(
            frame, text="💡 仅生成代码（不执行）",
            font=("Arial", 9), relief="flat",
            bg=self.COLORS["panel"], fg=self.COLORS["text"],
            command=self._code_only_mode, pady=4
        ).pack(fill="x", padx=4, pady=(0, 8))

    def _create_input_bar(self):
        bar = tk.Frame(self.root, bg=self.COLORS["sidebar"], pady=10)
        bar.pack(fill="x", padx=0, pady=0)

        inner = tk.Frame(bar, bg=self.COLORS["sidebar"])
        inner.pack(fill="x", padx=12)

        # 提示文字
        tk.Label(
            inner, text="💬",
            font=("Arial", 12),
            bg=self.COLORS["sidebar"], fg=self.COLORS["dim"]
        ).pack(side="left", padx=(0, 6))

        self.input_entry = tk.Entry(
            inner,
            font=("Consolas", 11),
            bg=self.COLORS["panel"], fg=self.COLORS["text"],
            insertbackground=self.COLORS["text"],
            relief="flat", borderwidth=0
        )
        self.input_entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 8))
        self.input_entry.bind("<Return>", self._send_message)
        self.input_entry.focus_set()

        self.send_btn = tk.Button(
            inner, text="发送  ↵",
            font=("Arial", 10, "bold"), relief="flat",
            bg=self.COLORS["accent"], fg="#1E1E2E",
            activebackground=self.COLORS["blue"],
            command=self._send_message, padx=14, pady=6
        )
        self.send_btn.pack(side="right")

    # ─────────────────────────────────────────────
    # 欢迎信息
    # ─────────────────────────────────────────────

    def _show_welcome(self):
        skills = self.agent.get_skill_list()
        self._append_chat("╔════════════════════════════════════╗\n", "dim")
        self._append_chat("  🔨 金锤子 GenForge 已启动\n", "bold")
        self._append_chat(f"  已加载技能: {', '.join(skills) if skills else '无'}\n", "dim")
        self._append_chat("╚════════════════════════════════════╝\n\n", "dim")
        self._append_chat("💡 示例指令：\n", "dim")
        self._append_chat("  • 画一面3000mm长、240mm厚的外墙\n", "dim")
        self._append_chat("  • 生成一个三室两厅的住宅轴网\n", "dim")
        self._append_chat("  • 创建A-WALL图层，颜色白色\n", "dim")
        self._append_chat("  • 在(0,0)到(6000,0)之间画一扇900mm宽的门\n\n", "dim")

    # ─────────────────────────────────────────────
    # 消息收发
    # ─────────────────────────────────────────────

    def _send_message(self, event=None):
        user_input = self.input_entry.get().strip()
        if not user_input:
            return

        self._append_chat(f"👤 你: {user_input}\n\n", "user")
        self.input_entry.delete(0, tk.END)
        self._set_input_state(False)
        self._reset_role_indicators()

        thread = threading.Thread(
            target=self._process_request,
            args=(user_input,),
            daemon=True
        )
        thread.start()

    def _process_request(self, user_input: str):
        """在后台线程中处理请求"""
        try:
            self.root.after(0, self._set_role_active, "Architect")
            result = self.agent.process_request(user_input)
            self.root.after(0, self._display_result, result)
        except Exception as e:
            self.root.after(0, self._append_chat, f"❌ 处理异常: {str(e)}\n\n", "error")
        finally:
            self.root.after(0, self._set_input_state, True)
            self.root.after(0, self._reset_role_indicators)

    def _code_only_mode(self):
        """仅生成代码，不执行"""
        user_input = self.input_entry.get().strip()
        if not user_input:
            messagebox.showinfo("提示", "请先在输入框中输入需求")
            return

        self._append_chat(f"👤 你（仅生成代码）: {user_input}\n\n", "user")
        self.input_entry.delete(0, tk.END)
        self._set_input_state(False)

        def task():
            result = self.agent.process_code_only(user_input)
            self.root.after(0, self._display_result, result)
            self.root.after(0, self._set_input_state, True)

        threading.Thread(target=task, daemon=True).start()

    def _execute_code(self):
        """执行代码面板中的代码"""
        code = self.code_text.get("1.0", tk.END).strip()
        if not code:
            messagebox.showinfo("提示", "代码面板为空")
            return

        self._append_chat("🚀 手动触发执行...\n", "compiler")
        self._set_input_state(False)

        def task():
            self.agent.last_generated_code = code
            result = self.agent.execute_last_code()
            self.root.after(0, self._display_result, result)
            self.root.after(0, self._set_input_state, True)

        threading.Thread(target=task, daemon=True).start()

    def _copy_code(self):
        code = self.code_text.get("1.0", tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(code)
        messagebox.showinfo("已复制", "代码已复制到剪贴板")

    # ─────────────────────────────────────────────
    # 结果展示
    # ─────────────────────────────────────────────

    def _display_result(self, result: dict):
        status = result.get("status", "error")

        # 建筑师计划
        plan = result.get("architect_plan")
        if plan:
            self._set_role_done("Architect")
            self._set_role_active("CADDeveloper")
            self._append_chat("🏛️  [建筑师] 绘图计划：\n", "architect")
            # 尝试美化 JSON
            try:
                plan_obj = json.loads(plan)
                plan_str = json.dumps(plan_obj, ensure_ascii=False, indent=2)
            except Exception:
                plan_str = plan
            self._append_chat(plan_str[:600] + ("..." if len(plan_str) > 600 else "") + "\n\n", "dim")

        # 生成的代码
        code = result.get("code")
        if code:
            self._set_role_done("CADDeveloper")
            self._set_role_active("Compiler")
            self._update_code_panel(code)
            self._append_chat(f"💻 [CAD开发] 代码生成完成 ({len(code)} 字符)\n\n", "developer")

        # 编译/执行结果
        if status == "success":
            self._set_role_done("Compiler")
            self._set_role_done("CAD")
            dll_path = result.get("dll_path", "")
            self._append_chat(f"✅ {result.get('message', '执行成功')}\n\n", "success")
            self._update_status(f"✅ 已连接 AutoCAD | {dll_path.split('/')[-1] if dll_path else ''}")

        elif status == "code_only":
            self._set_role_done("CADDeveloper")
            self._append_chat("💡 代码已生成，点击右侧「▶ 执行」发送到 CAD\n\n", "yellow")

        elif status == "error":
            self._append_chat(f"❌ 错误:\n{result.get('message', '未知错误')}\n\n", "error")

        else:
            self._append_chat(f"📋 {result.get('message', '')}\n\n", "dim")

    # ─────────────────────────────────────────────
    # UI 辅助方法
    # ─────────────────────────────────────────────

    def _append_chat(self, text: str, tag: str = ""):
        self.chat_text.config(state=tk.NORMAL)
        if tag:
            self.chat_text.insert(tk.END, text, tag)
        else:
            self.chat_text.insert(tk.END, text)
        self.chat_text.see(tk.END)
        self.chat_text.config(state=tk.DISABLED)

    def _update_code_panel(self, code: str):
        self.code_text.delete("1.0", tk.END)
        self.code_text.insert("1.0", code)

    def _set_input_state(self, enabled: bool):
        state = tk.NORMAL if enabled else tk.DISABLED
        self.input_entry.config(state=state)
        self.send_btn.config(state=state)

    def _update_status(self, text: str):
        self.status_var.set(text)

    def _set_role_active(self, role_id: str):
        """设置角色为「执行中」状态"""
        if role_id in self.role_labels:
            lbl, dot = self.role_labels[role_id]
            color = self.ROLES[role_id]["color"]
            lbl.config(fg=color, font=("Consolas", 9, "bold"))
            dot.config(text="●", fg=color)

    def _set_role_done(self, role_id: str):
        """设置角色为「完成」状态"""
        if role_id in self.role_labels:
            lbl, dot = self.role_labels[role_id]
            lbl.config(fg=self.COLORS["green"], font=("Consolas", 9))
            dot.config(text="✓", fg=self.COLORS["green"])

    def _reset_role_indicators(self):
        for role_id, (lbl, dot) in self.role_labels.items():
            lbl.config(fg=self.COLORS["dim"], font=("Consolas", 9))
            dot.config(text="○", fg=self.COLORS["dim"])

    def _refresh_skill_list(self):
        for widget in self.skill_frame.winfo_children():
            widget.destroy()

        skills = self.agent.get_skill_list()
        for skill in skills:
            tk.Label(
                self.skill_frame,
                text=f"  📖 {skill}",
                font=("Consolas", 8),
                bg=self.COLORS["sidebar"], fg=self.COLORS["text"],
                anchor="w"
            ).pack(fill="x", pady=1)

    def _reload_skills(self):
        self.agent.skills = self.agent.skill_loader.reload()
        self._refresh_skill_list()
        count = len(self.agent.skills)
        self._append_chat(f"🔄 技能已热重载，共 {count} 个技能\n\n", "dim")

    def _clear_history(self):
        self.agent.clear_history()
        self.chat_text.config(state=tk.NORMAL)
        self.chat_text.delete("1.0", tk.END)
        self.chat_text.config(state=tk.DISABLED)
        self._show_welcome()
        self._reset_role_indicators()

    # ─────────────────────────────────────────────
    # 运行
    # ─────────────────────────────────────────────

    def run(self):
        """启动主循环"""
        self.root.mainloop()
