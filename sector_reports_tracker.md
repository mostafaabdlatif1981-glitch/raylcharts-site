# تقارير القطاعات — رايل (تحديث أسبوعي كل جمعة)

آخر تحديث: إقفال الخميس 19/11/2026، والتوقعات لأسبوع 22–26 نوفمبر. اتنشرت كلها على raylcharts.com/reports يوم الجمعة 20/11/2026 بموافقة مصطفى.

- **التحديث:** كل جمعة على إقفال الخميس اللي قبلها.
- **التقسيم:** القطاعات والأسهم اللي فيها حسب تطبيق ثندر (Thndr).
- **الإجمالي:** 18 قطاع و226 سهم.

**الشكل:**
- صفحات للقطاع: الخلاصة، وجدول المقارنة، وأداء الأسبوع، والتوقعات، والترتيب.
- 4 صفحات لكل سهم.
- صفحة مصادر في الآخر.
- خلفية خضرا فاتحة، وخط رايل، والتقرير كله PDF.

## القطاعات والأسهم

| # | القطاع | مجلد الشغل | الأسهم | المستبعد |
|---|---|---|---|---|
| 1 | البنوك | sec1120h | COMI QNBE HDBK BQDC ADIB CANA FAIT CIEB EXPA SAUD UBEE | FAITA، EGBE، SAIB (بالدولار) |
| 2 | المواد الأساسية | sec1120k | EGAL MFPC ABUK FERC IRON EGCH SKPC EFIC ATQA ISMQ MICH KZPC ASCM ALUM | BIDI (مفيش تداول من يوليو) |
| 3 | العقارات | sec1120i | TMGH EMFD ORHD PHDC OCDI HELI MASR BONY ZMID PRDC ARAB ACAP AMER UNIT AIFI ELKA ACAMD ELSH DAPH ICID MENA NARE IDRE EHDR UEGC MAAL NHPS OBRI TANM RREI CCRS GIHD UTOP AREH ADRI UPMS FIRE | — |
| 4 | التكنولوجيا والاتصالات | sec1120 | ETEL EFIH FWRY OIH MPRC RACC DGTZ AMPI EGSA | — |
| 5 | الصناعات | sec1120b | SWDY GBCO ELEC GDWA DTPP MBEG EEII IBCT RKAZ | — |
| 6 | الأغذية والمشروبات | sec1120g | EAST EFID JUFO POUL OLFI SUGR DOMT AJWA AFMC GSSC WCDF UEFM INFI ZEOT MPCO EDFM ISMA CEFM SNFC MOSC MILS ADPC GGRN KRDI SCFM LUTS COSG EPCO ELNA NEDA | LUTS_R1 (حق اكتتاب) |
| 7 | الخدمات المالية | sec1120j | HRHO HALN RAYA BTFH VALU VLMRA CCAP BINV CICH CPME AMIA MOIN CNFN OFH ACTF ATLC DEIN AIH(=AIHC) ASPI ODIN PRMH EBSC AIDC ICLE AFDI TWSA TYCN KWIN EASB GRCA SEIG EOSB | NAHO، VLMR (بالدولار) • EGX30ETF، KASABF، EGREF (صناديق) |
| 8 | الرعاية الصحية | sec1120f | BIOC CLHO PHAR NIPH AMES ISPH RMDA MIPH CPCI MPCI AXPH NINH OCPH MCRO ADCI PHGC SIPC MEPA SPMD | FCMD (لسه مش متضاف، بياناته في ثندر) |
| 9 | المقاولات | sec1120l | ORAS KORA ENGC CRST GPIM AALR NCCW EALR WKOL IEEC GGCC HBCO FNAR INEG COPR | حق اكتتاب كورا (مش سهم) |
| 10 | النقل | sec1120d | ALCN CSAG ETRS | — |
| 11 | مواد البناء | sec1120e | ARCC SCEM MBSC MCQE SVCE LCSW ECAP CERA RUBX PRCL AMII | MISR (شطب اختياري) |
| 12 | التعليم | sec1120c | SCTS CIRA TALM CAED MOED | — |
| 13 | السياحة والترفيه | sec1120n | EGTS MHOT PHTV SDTI RTVC ROTO MMAT ELWA FTNS | GPPL، SPHT، TRTO (بالدولار) |
| 14 | التوزيع | sec1120r | MTIE IFAP GOUR MFSC ICFC SMFR GMCI VERT BIGP | — |
| 15 | السلع المعمرة (الغزل والنسيج) | sec1120q | ORWE SPIN KABO DSCW ACGC GTWL APSW | CFGH، GTEX (بالدولار) |
| 16 | المرافق | sec1120o | TAQA EGAS | — |
| 17 | الطاقة | sec1120m | AMOC | MOIL، NDRL (بالدولار) |
| 18 | الورق والتغليف | sec1120p | NAPR RAKT UNIP | MEGM (مفيش تداول من 2022)، EPPK (مفيش تداول من سبتمبر)، SIMO (مفيش تداول) |

## طريقة التحديث الأسبوعي (الجمعة)

1. **الوطنية للطباعة (NAPR):** مش موجودة على TradingView، فبياناتها بتتسحب من شارت ثندر X.
   - افتح السهم في ثندر من بحث مراقبة السوق.
   - الشارت: `document.querySelector('iframe[id^=tradingview]').contentWindow.tradingViewApi.activeChart().exportData({includeTime:true,includeSeries:true})`.
   - احفظ آخر 65 شمعة في `/home/claude/thndr/NAPR.txt` بالشكل `t,o,h,l,c,v;...`.
   - احسب المؤشرات (SMA20/50/100, RSI, ATR, Stoch, MACD, BB) واحفظها في `/home/claude/thndr/NAPR_ind.json`. القيمة السوقية من قايمة القطاع في ثندر.
2. **شغّل:** `python3 /home/claude/sec_weekly.py` (بيحدد آخر خميس لوحده).
   - بيبدّل كل التواريخ في الـ18 تقرير، ويسحب البيانات من TradingView، ويبني كل تقرير ويصوّره.
   - بيطلع قايمة BAD (أخطاء أو صفحات طالعة برا العرض)، وقايمة STALE (أسهم آخر شمعة فيها مش آخر جلسة، يعني موقوفة أو مفيش عليها تداول).
3. **راجع:** صفحتين من كذا تقرير. أي سهم بقى موقوف يتكتب ده في ملاحظته.
4. **انشر:** `python3 /home/claude/sec_weekly.py --publish`.
   - بيرفع ملفات PDF الجديدة، وبيحدث التواريخ وعدد الصفحات في reports.html وindex.html، وبيعمل commit وpush.
5. **ابعت لمصطفى ملخص بالعربي.**

**ملاحظات:**
- القيم العادلة والنتايج فاضلة من تحديث 12/11، لحد ما يتعمل تحديث جديد للقيم العادلة.
- عناوين أي ملخص لازم تكون بأرقام إيجابية، ومن غير عناوين خسارة.
