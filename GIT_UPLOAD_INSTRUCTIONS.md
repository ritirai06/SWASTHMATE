# GitHub पर Project Upload करने के लिए Step-by-Step Guide

## Step 1: GitHub पर नया Repository बनाएं

1. **https://github.com/ritirai06** पर जाएं
2. **"New"** या **"+"** (top right corner) पर क्लिक करें
3. **"New repository"** चुनें
4. **Repository name** दें (जैसे: `SWASTHMATE`)
5. **Description** (optional) दें - "Medical Report Analysis System using OCR, NLP, and AI"
6. **Public** या **Private** चुनें
7. ⚠️ **"Initialize this repository with a README"** को **UNCHECK** रखें (क्योंकि आपके पास पहले से code है)
8. **"Create repository"** पर क्लिक करें

## Step 2: Terminal में Commands चलाएं

GitHub repository बनने के बाद, आपको एक URL मिलेगा जैसे: 
`https://github.com/ritirai06/SWASTHMATE.git`

अब terminal में ये commands चलाएं (PowerShell में):

```powershell
# 1. Project folder में जाएं
cd "C:\Projects\SWASTHMATE"

# 2. Git remote add करें (YOUR_REPO_URL को अपने repository URL से replace करें)
git remote add origin https://github.com/ritirai06/SWASTHMATE.git

# 3. सभी files को stage करें
git add .

# 4. Commit करें
git commit -m "Initial commit: SWASTHMATE - Medical Report Analysis System"

# 5. Main branch को set करें (अगर पहले से नहीं है)
git branch -M main

# 6. GitHub पर push करें
git push -u origin main
```

## Important Notes:

- Repository name: `SWASTHMATE`
- अगर आप पहली बार GitHub पर push कर रहे हैं, तो आपको username और password (या Personal Access Token) देना होगा
- अगर 2FA enable है, तो Personal Access Token use करें

## Alternative: अगर repository पहले से बना है

अगर आपने repository पहले से बना लिया है और अब सिर्फ code push करना है:

```powershell
cd "C:\Projects\SWASTHMATE"
git remote add origin https://github.com/ritirai06/SWASTHMATE.git
git branch -M main
git push -u origin main
```

## Troubleshooting:

### अगर "remote origin already exists" error आए:
```powershell
git remote remove origin
git remote add origin https://github.com/ritirai06/SWASTHMATE.git
```

### अगर authentication error आए:
- GitHub पर Personal Access Token बनाएं: Settings → Developer settings → Personal access tokens
- Token को password की जगह use करें

