# GitHub 推送教程

## 目录
1. [快速开始](#快速开始)
2. [详细步骤](#详细步骤)
3. [后续 Git 操作](#后续-git-操作)
4. [常见问题](#常见问题)
5. [VS Code 集成操作](#vs-code-集成操作)

---

## 快速开始

如果你已经初始化了本地仓库，只需执行以下三个命令：

```bash
git add .                    # 添加所有文件到暂存区
git commit -m "提交信息"      # 提交到本地仓库
git push origin main         # 推送到远程仓库
```

---

## 详细步骤

### 第1步：配置 Git 全局设置

```bash
git config --global user.name "你的GitHub用户名"
git config --global user.email "你的邮箱@example.com"
```

### 第2步：初始化本地仓库

```bash
cd /Users/shilingjie/Desktop/ai/1017光伏电站消纳计算平台
git init
```

### 第3步：添加远程仓库

```bash
# 添加远程仓库
git remote add origin https://github.com/slingjie/xiaonajisuan.git

# 验证配置
git remote -v
```

**输出示例：**
```
origin  https://github.com/slingjie/xiaonajisuan.git (fetch)
origin  https://github.com/slingjie/xiaonajisuan.git (push)
```

### 第4步：添加文件到暂存区

```bash
# 添加所有文件
git add .

# 或添加特定文件
git add backend/
git add frontend/
git add docs/
```

### 第5步：提交到本地仓库

```bash
git commit -m "初始提交: 光伏电站消纳计算平台"
```

**提交信息建议：**
- ✅ `初始提交: 光伏电站消纳计算平台`
- ✅ `backend: 添加计算服务模块`
- ✅ `frontend: 优化仪表板图表展示`
- ❌ 避免：`update` 或 `fix bug`（信息过于简略）

### 第6步：推送到 GitHub

```bash
# 首次推送需要设置上游分支
git push -u origin main

# 之后推送只需
git push
```

**如果遇到大文件推送错误：**

```bash
# 增加 HTTP 缓冲区
git config --global http.postBuffer 524288000
git push origin main
```

---

## 后续 Git 操作

### 日常工作流程

#### 1. 创建功能分支

```bash
# 从 main 创建新分支
git checkout -b feature/new-feature-name

# 或使用新语法
git switch -c feature/new-feature-name
```

#### 2. 在分支上工作

```bash
# 编辑文件后，查看改动
git status

# 查看具体改动
git diff

# 提交改动
git add .
git commit -m "feature: 添加某功能"
```

#### 3. 提交到远程分支

```bash
# 首次推送
git push -u origin feature/new-feature-name

# 后续推送
git push
```

#### 4. 创建 Pull Request（在 GitHub 网页上）

- 访问 https://github.com/slingjie/xiaonajisuan
- 点击 "Compare & pull request"
- 填写标题和描述
- 点击 "Create pull request"

#### 5. 合并分支到 main

```bash
# 切换到 main 分支
git checkout main

# 拉取最新代码
git pull origin main

# 合并功能分支
git merge feature/new-feature-name

# 推送合并后的代码
git push origin main

# 删除已合并的分支
git branch -d feature/new-feature-name
git push origin -d feature/new-feature-name
```

### 同步远程更改

```bash
# 获取远程更新（不合并）
git fetch origin

# 拉取并合并（相当于 fetch + merge）
git pull origin main

# 如果有冲突，解决后再提交
git add .
git commit -m "解决合并冲突"
git push origin main
```

### 查看提交历史

```bash
# 查看提交日志
git log --oneline

# 查看详细信息
git log --graph --decorate --all

# 查看特定文件的历史
git log -- backend/app/main.py
```

### 撤销操作

#### 撤销未提交的改动

```bash
# 撤销某个文件
git checkout -- frontend/src/App.tsx

# 撤销所有改动
git reset --hard HEAD
```

#### 撤销已提交的改动

```bash
# 撤销上一次提交（保留改动）
git revert HEAD

# 完全删除上一次提交
git reset --hard HEAD~1

# 推送到远程
git push origin main --force-with-lease
```

#### 修改最后一次提交

```bash
# 修改提交信息
git commit --amend -m "新的提交信息"

# 添加遗漏的文件
git add forgotten_file.py
git commit --amend --no-edit
git push origin main --force-with-lease
```

### 分支管理

```bash
# 列出所有分支
git branch -a

# 切换分支
git checkout main
git switch main  # 新语法

# 删除本地分支
git branch -d feature/old-feature

# 删除远程分支
git push origin -d feature/old-feature

# 重命名分支
git branch -m old-name new-name
```

---

## 常见问题

### Q1: 推送时出现 "fatal: the remote end hung up unexpectedly"

**解决方案：**

```bash
# 增加缓冲区大小
git config --global http.postBuffer 524288000

# 重新推送
git push origin main
```

### Q2: 如何使用 SSH 而不是 HTTPS？

**生成 SSH 密钥：**

```bash
ssh-keygen -t ed25519 -C "your-email@example.com"
# 或
ssh-keygen -t rsa -b 4096 -C "your-email@example.com"
```

**添加公钥到 GitHub：**
1. 复制 `~/.ssh/id_ed25519.pub` 内容
2. 访问 https://github.com/settings/keys
3. 点击 "New SSH key" 粘贴

**修改远程地址：**

```bash
git remote set-url origin git@github.com:slingjie/xiaonajisuan.git
```

### Q3: 如何处理合并冲突？

```bash
# 拉取时出现冲突
git pull origin main

# VS Code 会显示冲突标记，编辑文件解决冲突

# 解决后提交
git add .
git commit -m "解决合并冲突"
git push origin main
```

### Q4: 如何回到之前的提交？

```bash
# 查看提交哈希
git log --oneline

# 回到特定提交（创建新分支）
git checkout -b restore-branch abc1234

# 或重置当前分支
git reset --hard abc1234
```

### Q5: 如何清理本地分支？

```bash
# 删除已合并的所有本地分支
git branch --merged | grep -v "\*" | xargs -n 1 git branch -d

# 同步删除远程已删除的分支
git fetch -p
```

---

## VS Code 集成操作

### 打开源代码管理面板

按 `Cmd + Shift + G`（macOS）或 `Ctrl + Shift + G`（Windows/Linux）

### VS Code 中的常见操作

| 操作 | 步骤 |
|------|------|
| **提交更改** | 1. 打开源代码管理 2. 输入提交信息 3. 点击 ✓ 或按 `Cmd + Enter` |
| **创建分支** | 1. 点击左下角分支名 2. 选择 "创建分支" 3. 输入分支名 |
| **切换分支** | 1. 点击左下角分支名 2. 从列表中选择 |
| **推送更改** | 1. 点击源代码管理中的 "..." 2. 选择 "推送" |
| **拉取更改** | 1. 点击源代码管理中的 "..." 2. 选择 "拉取" |
| **查看改动** | 1. 在源代码管理中点击文件 2. 对比视图显示改动 |
| **暂存文件** | 1. 在改动文件上点击 "+" 2. 文件移到暂存区 |
| **放弃改动** | 1. 在文件上点击 "..." 2. 选择 "放弃更改" |

### 推荐扩展

在 VS Code 中安装以下扩展提升 Git 体验：

- **GitLens** (`eamodio.gitlens`) - 查看行级代码历史
- **Git Graph** (`mhutchie.git-graph`) - 可视化分支图
- **GitHub Pull Requests and Issues** (`GitHub.vscode-pull-request-github`) - 直接在 VS Code 中管理 PR

---

## 最佳实践

### 提交规范

遵循 Conventional Commits 规范：

```
<type>(<scope>): <subject>

<body>

<footer>
```

**示例：**

```bash
git commit -m "feat(backend): 添加参数导入导出功能

- 支持 Excel 格式的参数导入
- 支持 JSON 格式的参数导出
- 添加参数验证逻辑

Closes #123"
```

**类型说明：**
- `feat`: 新功能
- `fix`: 修复问题
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 代码重构
- `perf`: 性能优化
- `test`: 添加或更新测试
- `chore`: 构建工具或依赖更新

### 分支命名规范

```
main                          # 生产环境主分支
develop                       # 开发分支
feature/user-authentication   # 新功能
bugfix/login-issue           # 修复 bug
hotfix/critical-production   # 紧急修复
release/v1.0.0              # 发布版本
```

### 每日工作流程示例

```bash
# 早上：拉取最新代码
git pull origin main

# 创建功能分支
git checkout -b feature/new-calculation

# 工作中：定期提交
git add backend/services/calculation.py
git commit -m "feat(calculation): 优化消纳计算算法"

# 推送到远程
git push origin feature/new-calculation

# 完成后：创建 Pull Request 在 GitHub 上
# 经过审核后合并到 main

# 清理本地分支
git checkout main
git pull origin main
git branch -d feature/new-calculation
```

---

## 总结

关键命令速查表：

```bash
# 初始化
git init
git remote add origin <URL>

# 日常
git add .
git commit -m "message"
git push origin main

# 分支
git checkout -b feature/name    # 创建分支
git push -u origin feature/name # 推送分支
git merge feature/name          # 合并分支

# 查看
git status                      # 查看状态
git log --oneline              # 查看历史
git diff                       # 查看改动
```

祝你使用愉快！有问题可参考 [GitHub 官方文档](https://docs.github.com) 或在 VS Code 中安装 GitLens 扩展获得更多帮助。
