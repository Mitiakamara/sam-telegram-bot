# 📦 How to Add Other Repositories to Workspace

## Option 1: Clone as Subdirectories (Recommended)

This keeps all three repositories in one workspace, making it easy to navigate between them.

### Steps:

1. **Open terminal in the workspace** (or use Cursor's integrated terminal)

2. **Navigate to workspace root**:
   ```bash
   cd /workspace
   ```

3. **Clone the repositories**:
   ```bash
   # Clone sam-gameapi
   git clone https://github.com/YOUR_USERNAME/sam-gameapi.git
   
   # Clone sam-srdservice
   git clone https://github.com/YOUR_USERNAME/sam-srdservice.git
   ```

   Or if they're private repositories:
   ```bash
   git clone git@github.com:YOUR_USERNAME/sam-gameapi.git
   git clone git@github.com:YOUR_USERNAME/sam-srdservice.git
   ```

4. **Verify structure**:
   ```
   /workspace/
   ├── sam-telegram-bot/  (current repo)
   ├── sam-gameapi/       (new)
   └── sam-srdservice/    (new)
   ```

### Pros:
- ✅ All repos in one place
- ✅ Easy to navigate in Cursor
- ✅ Can edit files across repos
- ✅ Simple git operations

### Cons:
- ⚠️ Need to manage multiple git repos
- ⚠️ Slightly larger workspace

---

## Option 2: Git Submodules (Advanced)

This keeps them as separate repos but linked to this one.

### Steps:

1. **Add as submodules**:
   ```bash
   cd /workspace
   git submodule add https://github.com/YOUR_USERNAME/sam-gameapi.git sam-gameapi
   git submodule add https://github.com/YOUR_USERNAME/sam-srdservice.git sam-srdservice
   ```

2. **Initialize submodules**:
   ```bash
   git submodule update --init --recursive
   ```

### Pros:
- ✅ Proper git relationship between repos
- ✅ Can track specific commits

### Cons:
- ⚠️ More complex git operations
- ⚠️ Need to remember to update submodules

---

## Option 3: Side-by-Side Directories

Clone them outside but at the same level.

### Steps:

1. **Navigate to parent directory**:
   ```bash
   cd /workspace/..
   # or wherever you want them
   ```

2. **Clone repositories**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/sam-gameapi.git
   git clone https://github.com/YOUR_USERNAME/sam-srdservice.git
   ```

3. **Add to Cursor workspace**:
   - File → Add Folder to Workspace
   - Select each repository folder

### Pros:
- ✅ Keeps repos separate
- ✅ Can open in same workspace

### Cons:
- ⚠️ Need to manage workspace configuration
- ⚠️ Paths might be more complex

---

## Option 4: Use Cursor's Multi-Root Workspace

1. **File → Add Folder to Workspace**
2. **Navigate to and select each repository folder**
3. **Save workspace** (File → Save Workspace As)

This creates a `.code-workspace` file that includes all three repos.

---

## Recommended: Option 1 (Clone as Subdirectories)

This is the simplest and most straightforward approach.

### Quick Command:

```bash
cd /workspace
git clone https://github.com/YOUR_USERNAME/sam-gameapi.git
git clone https://github.com/YOUR_USERNAME/sam-srdservice.git
```

**Replace `YOUR_USERNAME` with your actual GitHub username or organization.**

---

## After Adding Repositories

Once the repositories are added, I'll be able to:

1. ✅ Read their code structure
2. ✅ Understand their APIs
3. ✅ See their endpoints and data models
4. ✅ Plan proper integration
5. ✅ Ensure compatibility
6. ✅ Implement the conversational system correctly

---

## If Repositories Are Private

If the repositories are private, you'll need to:

1. **Set up SSH keys** (if using SSH):
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   # Add to GitHub SSH keys
   ```

2. **Or use HTTPS with token**:
   ```bash
   git clone https://YOUR_TOKEN@github.com/YOUR_USERNAME/sam-gameapi.git
   ```

3. **Or configure git credentials**:
   ```bash
   git config --global credential.helper store
   # Then clone normally, enter credentials once
   ```

---

## Verification

After cloning, verify I can see them:

```bash
ls -la /workspace/
```

You should see:
- `sam-telegram-bot/` (or current directory contents)
- `sam-gameapi/`
- `sam-srdservice/`

Then I can immediately start analyzing their structure and planning integration!

---

## Need Help?

If you encounter any issues:
- **Permission errors**: Check repository access
- **Authentication errors**: Set up SSH keys or use HTTPS with token
- **Not found errors**: Verify repository names and URLs

Let me know once they're added and I'll start analyzing! 🚀
