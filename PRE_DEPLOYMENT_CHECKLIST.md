# 📋 Pre-Deployment Checklist

Use this checklist before deploying your HR Agent to ensure everything works smoothly.

## ✅ Code Quality

- [ ] All Python files have no syntax errors
- [ ] All imports are working correctly
- [ ] No hardcoded file paths (use relative paths)
- [ ] No print statements (use logging or st.write)
- [ ] Code is properly formatted and commented

## ✅ Dependencies

- [ ] All packages listed in `requirements.txt`
- [ ] No version conflicts
- [ ] Tested with: `pip install -r requirements.txt`
- [ ] All imports work after fresh install

## ✅ Data Files

- [ ] Data files are in correct location (`data/` folder)
- [ ] File paths are relative, not absolute
- [ ] CSV files are not corrupted
- [ ] Data files are not too large (< 100MB for Streamlit Cloud)

## ✅ Environment Variables

- [ ] `.env` file is in `.gitignore` (CRITICAL!)
- [ ] No AWS credentials in code
- [ ] App works without AWS credentials (fallback mode)
- [ ] Environment variables documented

## ✅ Git Repository

- [ ] Git initialized: `git init`
- [ ] All files added: `git add .`
- [ ] Changes committed: `git commit -m "message"`
- [ ] Remote added: `git remote add origin <url>`
- [ ] Pushed to GitHub: `git push -u origin main`
- [ ] Repository is public (for Streamlit Cloud)

## ✅ Local Testing

- [ ] App runs locally: `streamlit run app.py`
- [ ] All features work correctly
- [ ] No errors in console
- [ ] UI displays properly
- [ ] Data loads successfully
- [ ] All buttons and interactions work

## ✅ Deployment Files

- [ ] `requirements.txt` exists and is complete
- [ ] `Procfile` created (for Heroku)
- [ ] `runtime.txt` created (for Heroku)
- [ ] `Dockerfile` created (for Docker)
- [ ] `.dockerignore` created (for Docker)
- [ ] `.gitignore` properly configured

## ✅ Security

- [ ] No API keys in code
- [ ] No passwords in code
- [ ] `.env` file not committed
- [ ] Sensitive data not in repository
- [ ] AWS credentials configured in deployment platform (not in code)

## ✅ Documentation

- [ ] README.md exists and is up-to-date
- [ ] Deployment instructions clear
- [ ] Features documented
- [ ] Known issues documented
- [ ] Contact information included

## ✅ Performance

- [ ] App loads in reasonable time (< 10 seconds)
- [ ] No memory leaks
- [ ] Large computations are cached
- [ ] Data loading is optimized
- [ ] UI is responsive

## ✅ Streamlit Specific

- [ ] No duplicate element IDs (all plotly charts have unique keys)
- [ ] Page config set correctly
- [ ] Caching used appropriately (`@st.cache_data`)
- [ ] Session state managed properly
- [ ] No blocking operations in main thread

## ✅ Final Checks

- [ ] Test deployment on chosen platform
- [ ] Verify all features work on deployed app
- [ ] Check logs for errors
- [ ] Test on different browsers
- [ ] Test on mobile (if applicable)
- [ ] Share URL works correctly
- [ ] App doesn't crash under load

## 🚀 Ready to Deploy!

Once all items are checked, you're ready to deploy!

### Quick Deploy Commands:

**Windows:**
```bash
deploy.bat
```

**Linux/Mac:**
```bash
chmod +x deploy.sh
./deploy.sh
```

**Or manually:**
```bash
# Push to GitHub
git push origin main

# Then deploy on Streamlit Cloud:
# https://share.streamlit.io/
```

---

## 🐛 Common Issues

### Issue: Import errors after deployment
**Solution:** Add missing packages to `requirements.txt`

### Issue: File not found errors
**Solution:** Use relative paths, not absolute paths

### Issue: App crashes on startup
**Solution:** Check logs in deployment platform dashboard

### Issue: Slow performance
**Solution:** Add caching with `@st.cache_data` decorator

### Issue: Out of memory
**Solution:** Reduce dataset size or upgrade deployment tier

---

## 📞 Need Help?

- Check **DEPLOYMENT_GUIDE.md** for detailed instructions
- Check **QUICK_DEPLOY.md** for fast deployment
- Visit Streamlit Community: https://discuss.streamlit.io/
- Check deployment platform docs

---

Good luck! 🎉
