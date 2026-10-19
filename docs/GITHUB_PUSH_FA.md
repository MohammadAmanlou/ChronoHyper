# دستورالعمل سریع برای Push کردن پروژه به GitHub (خصوصی)

حساب GitHub متصل به ChatGPT: **MohammadAmanlou**. چون داده‌ها و پاسخ‌های مرجع را Constructor ارائه کرده است، این مخزن را **Private** بساز. فایل‌های خصوصی/کد استاد را بدون اجازه عمومی منتشر نکن.

۱. فایل ZIP جدید `Constructor_CKL_GitHub_Ready_2026-10-19.zip` را استخراج کن. داخل آن یک پوشه به نام `constructor-ckl-research` است. پوشه را در VS Code باز کن. مسیر ریشه باید شامل `README.md`, `src`, `research_lab`, `outputs_selected` باشد.

۲. در مرورگر با حساب `MohammadAmanlou` به <https://github.com/new> برو؛ نام `constructor-ckl-research`، حالت **Private**، بدون افزودن README/License/.gitignore؛ مخزن را بساز.

۳. در ترمینال PowerShell ریشه پوشه استخراج‌شده، این دستورها را *یکی‌یکی* اجرا کن:

```powershell
git --version
git init -b main
git add .
git status --short
git commit -m "Initial verified temporal hypergraph research snapshot"
git remote add origin https://github.com/MohammadAmanlou/constructor-ckl-research.git
git push -u origin main
```

اگر خطای نام/ایمیل گیت گرفتی، حساب Git خودت را تنظیم کن:

```powershell
git config --global user.name "Mohammad Amanlou"
git config --global user.email "mohammadamanlou2@gmail.com"
```

GitHub ممکن است صفحه مرورگر برای ورود باز کند. از **Git Credential Manager** استفاده کن؛ نیازی نیست رمز یا توکن را در چت بفرستی.

۴. به <https://github.com/MohammadAmanlou/constructor-ckl-research> برو؛ بالای مخزن باید **Private** دیده شود و `report.pdf`, `metrics.json`, `research_outputs/model_lock.json`, `outputs_selected` و `AI_USAGE.md` وجود داشته باشند.

۵. بعد از Push، فقط **لینک مخزن** را در همین چت بفرست. حساب GitHub هم‌اکنون به ChatGPT متصل است، ولی شاید لازم شود برای مخزن جدید از **Settings → Plugins → GitHub** اجازه دسترسی بدهی.

**وضعیت علمی:** این ZIP کامل‌ترین نسخه تجمیع‌شده فعلی برای ادامه پژوهش است؛ هنوز ادعای «تحویل نهایی بدون نقص» ندارد. ۱۲ عنوان اشتباه، ۲۸ عنوان مبهم و ۴۰ توضیح با برچسب نامعلوم ثبت شده‌اند؛ در ادامه با یک شاخه جداگانه اصلاحشان می‌کنیم. گزارش اصلی فعلی چهارصفحه‌ای و متناسب با مدل قفل‌شده است، نه نسخه قدیمی.

**توجه:** Push کردن به مخزن **خصوصی** به معنای تحویل به استاد یا اکاترینا نیست؛ لینک خصوصی بدون دعوت و دسترسی قابل مشاهده برای آن‌ها نیست. برای ارسال رسمی، مهلت و روش تحویل را از ایمیل اصلی پیگیری کن.
