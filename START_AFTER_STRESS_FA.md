# Constructor — ادامه دقیق بعد از 65 اجرای توسعه و 5 آزمون فشار

**این بسته کمکی را داخل پوشه `constructor-tkh-research` کپی کن. نه اصل کد و نه نتایج فعلی را پاک یا بازنویسی نکن.**

## چه چیزی واقعاً انجام شده است؟
- 65/65 مدل-بذر مرحله DEVELOPMENT روی 2020/2022/2024 به گزارش کاربر کامل شده‌اند (13×5×3 = 195 برازش).
- خط‌مبنای `clique_pairwise` با پنج بذر کامل شده؛ هنوز دستور aggregate جداگانه لازم است.
- آزمون فشار هر پنج روش انجام شده، اما هیچ null p ضعیف‌تر از 0.05 نیست. `null_p`های 1.00، .75، .65، .25، .70 *معناداری برتری* محسوب نمی‌شوند.
- تأیید نهایی روی مقالات رزروشده، بازبینی انسانی برچسب‌ها، گزارش و ارسال به دانشگاه هنوز توسط کاربر تأیید نشده‌اند.

## 0 — تثبیت نتایج موجود و بررسی فایل‌ها
در PowerShell از ریشه پروژه پژوهشی:

```powershell
Copy-Item .\research_outputs\final_matrix\experiment_registry.csv .\research_outputs\experiment_registry_backup.csv -Force
Get-ChildItem .\research_outputs\final_matrix\stress\*\result.json
```

## 1 — تجمیع پنج اجرای Pairwise

```powershell
.\.venv\Scripts\python.exe -m research_lab.aggregate --out research_outputs/projection_5seed --reference clique_pairwise
Import-Csv .\research_outputs\projection_5seed\method_summary.csv | Where-Object { $_.year -eq '2024' } | Format-Table -AutoSize
```

نتیجه محاسبه‌شده از لاگ فعلی: سال 2024 میانگین pairwise cut≈0.62193، title≈0.11671، ARI≈0.31367؛ این تنها یک baseline بدون وزن‌دهی مناسب به اندازه ابر‌یال است، نه رقابت نهایی با همه الگوریتم‌های گرافی.

## 2 — تحلیل قبل از تصمیم
- فایل‌های `research_outputs/final_matrix/method_summary.csv`، `paired_paper_bootstrap.csv`، `RESEARCH_COMPARISON_REPORT.md` و `research_outputs/projection_5seed/method_summary.csv` را با هم بررسی کن.
- از پوشه `research_outputs/final_matrix/stress` پنج فایل `result.json` برای روش‌های semantic_kmeans, incidence_svd, native_joint_70, native_temporal_08, native_temporal_20 را بررسی کن.
- از همان داده توسعه یک دلیل مکتوب انتخاب بنویس. `native_temporal_20` تنها **نامزد قابل دفاع** است نه یک «برنده اثبات‌شده»: ARI بالاتر، عملکرد ضعیف‌تر از semantic baseline در cut، frozen trivial ARI=1 و null-p ناکافی را هم بنویس. اگر مدل دیگری انتخاب شد، شناسه آن را در همه فرمان‌های پایین جایگزین کن.

## 3 — قفل‌کردن روش فقط یک بار، *قبل از هر تأیید*

```powershell
.\.venv\Scripts\python.exe -m research_lab.lock_selection --development research_outputs/final_matrix --method native_temporal_20 --out research_outputs/model_lock.json
Get-Content .\research_outputs\model_lock.json
```

- اگر lock قبلاً وجود دارد، **پاکش نکن**؛ استفاده از مدل دیگر پس از مشاهده نتیجه تأییدی مستلزم اعلام مطالعه اکتشافی جدید است.
- مدل قفل‌شده ممکن است با جدول تو متفاوت انتخاب شود؛ توصیه فوق مشروط است.

## 4 — یک بار آزمایش تأییدی روی منبع مقاله‌های رزروشده

```powershell
powershell -ExecutionPolicy Bypass -File .\run_research_pipeline.ps1 -Phase confirmation -ChosenMethod native_temporal_20
Import-Csv .\research_outputs\confirmation\experiment_registry.csv | Group-Object status | Select-Object Name,Count
```

انتظار: `complete=5` و صفر شکست؛ فایل‌های `confirmation/paper_split.json`, `protocol.json`, `method_summary.csv` و `RESEARCH_COMPARISON_REPORT.md` را نگه‌دار. تقسیم داده transductive است؛ «مقالات جدید خارج از مجموعه» نیست.

## 5 — تبدیل خروجی *همین* روش قفل‌شده به سلسله‌مراتب کامل
سه اسکریپت همراه بسته را در ریشه پروژه کپی کن. سپس:

```powershell
.\.venv\Scripts\python.exe .\export_locked_full_hierarchy.py --lock research_outputs/model_lock.json --confirmation research_outputs/confirmation --seed 17 --out outputs_selected --with-2025
.\.venv\Scripts\python.exe .\verify_selected_outputs.py --out outputs_selected
```

نتیجه شامل hierarchy_2020/2022/2024/2025.json، label_evidence، collapsed_edges، temporal_events، selected_export_manifest و **بازیابی ۲۰۲۵ با برچسب EXPLORATORY** است. بدون تغییر افرازهای قفل‌شده 2020/22/24 و بدون تغییر outputs اصلی.

محدودیت ضروری: ابزار فقط P1/P2/P4 و بخش‌های T3/T5 را به خروجی روش منتخب وصل می‌کند؛ ارزیابی مستقل معنایی، معناداری آماری و گزارش جدید را اثبات نمی‌کند.

## 6 — ساخت فرم انسانیِ برچسب‌ها از خروجی جدید

```powershell
.\.venv\Scripts\python.exe .\selected_label_audit.py make --project .
```

فایل `outputs_selected/label_review_sheet.csv` ساخته می‌شود. ۴۸ ردیف را شخصاً یا ترجیحاً با داور مستقل با شواهد واقعی پر کن؛ فیلدهای `accurate/vague/wrong`, `yes/no/unclear`, `yes/no` و نام داور را تکمیل کن. سپس:

```powershell
.\.venv\Scripts\python.exe .\selected_label_audit.py score --file outputs_selected/label_review_sheet.csv
```

نتیجه `outputs_selected/label_review_results.json`. اگر همه ۴۸ ردیف ارزیابی نشده‌اند این را به وضوح در گزارش بیان کن. «ادعای درست با جملات سطحیِ عضویت» با «برچسب علمی غنی و مفید» فرق دارد.

## 7 — کیفیت کاربردی و کنترل نشت داده
- فایل `outputs_selected/selected_retrieval_EXPLORATORY_2025.json` فقط ۱۴ پرسش A را امتیازدهی کرده؛ چهار پرسش نوع B ارزیابی نشده‌اند. سؤالات و پاسخ‌ها قبلاً بررسی شده‌اند، بنابراین این معیار آزمون کاملاً تازه نیست.
- مقایسه‌ها را روی تعداد واقعی محاسبات شباهت و مدت‌زمان اجرای بازیابی انجام بده، نه شمارش انتخاب‌های پس از رتبه‌بندی کامل. اگر روش تخت بهتر شد، شکست را ثبت کن.
- گروه تأیید مقاله‌ها برای fitting کنار گذاشته شده‌اند اما *نام سطحی همه موجودیت‌ها به‌شکل transductive دیده شده*؛ این را گزارش کن.

## 8 — آخرین گزارش و نمودار
- گزارش 3–5 صفحه‌ای انگلیسی جدید بنویس. قالب اصلی `report.md` قدیمی را مستقیم کپی نکن: آن برای روش native_temporal_08 و تقسیم 80/20 بوده و اعدادش برای این خروجی معتبر نیستند.
- جدول روش‌ها با پنج بذر، نتیجه کنترل دوتایی، جداول دو هدف متناقض، pهای نامعنادار، حساسیت زمانی و هزینه اجرا را وارد کن.
- نمودارهای همه روش‌ها و شکست‌ها را در appendix / registry بگذار.
- توصیف استفاده از AI را در `AI_USAGE.md` به‌روز کن؛ مقاله‌هایی را که واقعاً خواندی و روش‌هایی را که واقعاً اجرا کردی از هم تفکیک کن.
- از `outputs_selected` داده‌های hierarchy و JSON را همراه گزارش جدید و کد نصب‌شدنی + README در بسته بگذار.

## 9 — بسته‌بندی صحیح، بدون محیط مجازی
از روی کپی تمیز پروژه خروجی نهایی آماده کن. `.venv`, `__pycache__`, temp و بکاپ‌ها را ارسال نکن. اطمینان حاصل کن `README.md` و commands با همین ساختار مطابقت دارند و همه JSONها از همان مدل انتخابی ساخته شده‌اند.

## 10 — محدودیت مهلت
مهلت توافق‌شده دانشگاه **دوشنبه 19 اکتبر 2026** و ساعت دقیق نامشخص است. هنوز ارسال نهایی در حساب Gmail محمد تأیید نشده بود. اگر انجام کار جدید سبب از دست رفتن مهلت می‌شود، ارسال نسخه سالمِ قبلی با ذکر محدودیت‌ها و درخواست اجازه برای نسخه تکمیلی را در اولویت قرار بده. هیچ قبولی یا تمدیدی را بدون مستندات فرض نکن.
