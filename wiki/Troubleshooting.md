# 🔧 Troubleshooting

Common issues and solutions for FlashGenie v1.5.

## 🚨 **Installation Issues**

### **Python Version Error**
```
Error: Python 3.8+ required
```
**Solution**: 
- Check Python version: `python --version`
- Install Python 3.8+ from [python.org](https://python.org)
- Use `python3` command if multiple versions installed

### **Permission Denied**
```
Permission denied: pip install
```
**Solutions**:
- Use virtual environment: `python -m venv flashgenie_env`
- Install for user only: `pip install --user -r requirements.txt`
- Use `sudo` on Linux/Mac (not recommended)

### **Module Not Found**
```
ModuleNotFoundError: No module named 'flashgenie'
```
**Solutions**:
- Ensure you're in the FlashGenie directory
- Check dependencies: `pip install -r requirements.txt`
- Verify installation: `python -m flashgenie --version`

## 🎮 **Command Issues**

### **Deck Not Found**
```
Error: Deck 'My Deck' not found
```
**Solutions**:
- Check deck names: `python -m flashgenie list`
- Use exact deck name (case-sensitive)
- Create deck first: `python -m flashgenie create "My Deck"`

### **No Cards Due**
```
No cards are due for review
```
**Solutions**:
- Add more cards: `python -m flashgenie add "Deck Name"`
- Import cards: `python -m flashgenie import "Deck" file.csv`
- Force review: `python -m flashgenie quiz "Deck" --cards 10`

### **Import Failed**
```
Error importing file: Invalid format
```
**Solutions**:
- Check file format (CSV, TXT, JSON supported)
- Verify file encoding (UTF-8 recommended)
- Check CSV structure: Question,Answer,Tags columns
- Use `--preview` to test import first

## 🧠 **AI Feature Issues**

### **Adaptive Planning Not Working**
```
Error: Unable to create adaptive plan
```
**Solutions**:
- Ensure deck has enough cards (minimum 5)
- Check card difficulty distribution
- Verify recent study history exists
- Try basic planning first

### **Velocity Tracking Unavailable**
```
Insufficient data for velocity analysis
```
**Solutions**:
- Study for at least 3 sessions
- Complete full study sessions
- Ensure cards have review history
- Wait for more data accumulation

### **Knowledge Graph Empty**
```
No relationships found for knowledge graph
```
**Solutions**:
- Add tags to your cards
- Use hierarchical tags (parent:child)
- Study cards to build relationships
- Import cards with auto-tagging

## 📊 **Performance Issues**

### **Slow Response Times**
**Solutions**:
- Close other applications
- Reduce deck size for testing
- Check available memory
- Update to latest version

### **Large File Import Slow**
**Solutions**:
- Import in smaller batches
- Use `--preview` to test first
- Ensure sufficient disk space
- Consider file encoding (UTF-8 fastest)

### **Memory Usage High**
**Solutions**:
- Restart FlashGenie periodically
- Reduce concurrent operations
- Clear old session data
- Check for memory leaks (report if found)

## 💾 **Data Issues**

### **Data Corruption**
```
Error: Unable to load deck data
```
**Solutions**:
- Check backup files in `data/backups/`
- Restore from export: `python -m flashgenie import "Deck" backup.json`
- Verify file permissions
- Report corruption for investigation

### **Missing Achievements**
```
Achievements not updating
```
**Solutions**:
- Complete full study sessions
- Check achievement requirements
- Restart FlashGenie
- Verify data directory permissions

### **Export Failed**
```
Error: Unable to export deck
```
**Solutions**:
- Check disk space
- Verify write permissions
- Use different output location
- Try different export format

## 🔒 **Security & Privacy**

### **Data Location Concerns**
**Question**: Where is my data stored?
**Answer**: All data is stored locally in the `data/` directory. No data is sent to external servers.

### **Backup Recommendations**
- Regular backups: `python -m flashgenie backup`
- Export important decks: `python -m flashgenie export "Deck" backup.json`
- Copy `data/` directory for full backup

## 🐛 **Reporting Bugs**

### **Before Reporting**
1. Check this troubleshooting guide
2. Search [GitHub Issues](https://github.com/himent12/FlashGenie/issues)
3. Try reproducing with minimal example
4. Gather system information

### **Bug Report Template**
```
**System Information:**
- OS: [Windows/macOS/Linux]
- Python version: [3.8/3.9/3.10/etc.]
- FlashGenie version: [1.5.0]

**Issue Description:**
[Clear description of the problem]

**Steps to Reproduce:**
1. [First step]
2. [Second step]
3. [Third step]

**Expected Behavior:**
[What should happen]

**Actual Behavior:**
[What actually happens]

**Error Messages:**
[Any error messages or logs]

**Additional Context:**
[Any other relevant information]
```

## 🔧 **Advanced Troubleshooting**

### **Debug Mode**
```bash
# Enable verbose logging
python -m flashgenie --debug quiz "Deck Name"

# Check log files
cat data/flashgenie.log
```

### **Configuration Reset**
```bash
# Reset to default settings
python -m flashgenie config reset

# Backup current config first
python -m flashgenie config export config_backup.json
```

### **Clean Installation**
```bash
# Remove all data (backup first!)
rm -rf data/

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Verify clean installation
python -m flashgenie --version
```

## 📞 **Getting Help**

### **Community Support**
- **GitHub Discussions**: [Ask questions](https://github.com/himent12/FlashGenie/discussions)
- **GitHub Issues**: [Report bugs](https://github.com/himent12/FlashGenie/issues)
- **Wiki**: [Browse documentation](Home.md)

### **Self-Help Resources**
- **[FAQ](FAQ.md)**: Common questions and answers
- **[Complete Command Reference](Complete-Command-Reference.md)**: All commands
- **[Configuration Options](Configuration-Options.md)**: Settings guide

### **Professional Support**
For institutional or commercial support needs, contact through GitHub Issues with "Support Request" label.

---

**Still having issues?** Don't hesitate to ask for help in [GitHub Discussions](https://github.com/himent12/FlashGenie/discussions) - the community is here to help! 🧞‍♂️✨
