# Search Comparison Report

**Date:** 2026-06-03  
**Index:** `english-mxbai` — English hadiths + bilingual pairs  
**isChainRef filter:** always applied (pure isnad chains excluded)  
**Grade flags:** ⚠️ = Da'if or Maudu' | 🔗 = isChainRef (would be excluded)  
**Grade reason:** auto-Sahih for Bukhari/Muslim; otherwise from raw grade field  


---
## Part 1 — Routing Verification

Checks which route the query router selects for each query.
English queries should only return `lang:en` docs; Arabic queries return all.

| Query | Route | lang dist (top 10) | Correct? |
|-------|-------|-------------------|---------|
| `comparing yourself to others` | lexical | en:10 ar:0 | ✅ |
| `aisha` | lexical | en:10 ar:0 | ✅ |
| `"actions are by intention"` | lexical_phrase | en:1 ar:0 | ✅ |
| `actions are by intention` | lexical | en:10 ar:0 | ✅ |
| `how to make wudu` | lexical | en:10 ar:0 | ✅ |
| `ramadan` | lexical | en:10 ar:0 | ✅ |
| `music` | lexical | en:10 ar:0 | ✅ |
| `الرحمن` | lexical_arabic | en:10 ar:0 | ✅ |
| `الرحمان` | lexical_arabic | en:10 ar:0 | ✅ |
| `الرحمٰن` | lexical_arabic | no hits | ❌ no hits |
| `الرحمن قد اشتق من الرحم` | lexical_arabic | en:10 ar:0 | ✅ |

---
## Part 2 — BM25: hadithText vs englishMatn

**hadithText** = full hadith including isnad prefix ("Narrated X that Y said…").
**englishMatn** = body only, isnad stripped (cleaner signal, smaller vocab match).


### `comparing yourself to others`


#### hadithText (BM25)

_3,848 total matches_

1. **muslim:1776 d**  `Sahih` _(raw: — | Muslim collection (auto-Sahih))_  
   This hadith has been narrated on the authority of Bara' with another chain of transmitters, but this hadith is…  
   score: 13.204

2. **abudawud:4627**  `Sahih` _(raw: Sahih | graded: Sahih)_  
   Ibn ‘Umar said: We used to say in the times of the Prophet (saws): We do not compare anyone with Abu Bakr. ’Um…  
   score: 11.855

3. **muslim:2431**  `Sahih` _(raw: — | Muslim collection (auto-Sahih))_  
   Abu Musa reported Allah's Messenger (may peace be upon him) as saying: There are many persons amongst men who …  
   score: 11.358

4. **bukhari:3334**  `Sahih` _(raw: — | Bukhari collection (auto-Sahih))_  
   Narrated Anas: The Prophet said, "Allah will say to that person of the (Hell) Fire who will receive the least …  
   score: 11.310

5. **abudawud:356**  `Hasan` _(raw: Hasan | graded: Hasan)_  
   'Uthaim b. Kulaib reported from his father (Kuthair) on the authority of his grandfather (Kulaib) that he came…  
   score: 10.787

6. **mishkat:48**  `Uncategorized` _(raw: [{"graded_by": "Zubair `Aliza'i", "grade": "Isn\u0101d Da'\u | graded: Isn\u0101d Da'\u012bf)_  
   He also said that he asked the Prophet what was the most excellent aspect of faith, and received the reply, “T…  
   score: 10.425

7. **mishkat:6025**  `Uncategorized` _(raw: — | no grade data)_  
   Ibn 'Umar said: In the time of the Prophet, we did not compare anyone with Abu Bakr. `Umar came next and then …  
   score: 10.412

8. **muslim:2939 b**  `Sahih` _(raw: — | Muslim collection (auto-Sahih))_  
   Mughira b. Shu'ba reported that none asked Allah's Apostle (may peace be upon him) about Dajjal more than I as…  
   score: 10.027

9. **bukhari:4816**  `Sahih` _(raw: — | Bukhari collection (auto-Sahih))_  
   Narrated Ibn Mas`ud: (regarding) the Verse: 'And you have not been screening against yourself lest your ears, …  
   score: 9.915

10. **bukhari:6557**  `Sahih` _(raw: — | Bukhari collection (auto-Sahih))_  
   Narrated Anas bin Malik: The Prophet said, "Allah will say to the person who will have the minimum punishment …  
   score: 9.421


#### englishMatn (BM25)

_10,000 total matches_

1. **bukhari:3334**  `Sahih` _(raw: — | Bukhari collection (auto-Sahih))_  
   Narrated Anas: The Prophet said, "Allah will say to that person of the (Hell) Fire who will receive the least …  
   score: 12.499

2. **bukhari:6557**  `Sahih` _(raw: — | Bukhari collection (auto-Sahih))_  
   Narrated Anas bin Malik: The Prophet said, "Allah will say to the person who will have the minimum punishment …  
   score: 10.536

3. **muslim:2636 a**  `Sahih` _(raw: — | Muslim collection (auto-Sahih))_  
   Abu Huraira reported that a woman came to Allah's Apostle (may peace be upon him) with her child and said: All…  
   score: 9.499

4. **bukhari:4816**  `Sahih` _(raw: — | Bukhari collection (auto-Sahih))_  
   Narrated Ibn Mas`ud: (regarding) the Verse: 'And you have not been screening against yourself lest your ears, …  
   score: 9.442

5. **abudawud:356**  `Hasan` _(raw: Hasan | graded: Hasan)_  
   'Uthaim b. Kulaib reported from his father (Kuthair) on the authority of his grandfather (Kulaib) that he came…  
   score: 8.628

6. **bukhari:5797**  `Sahih` _(raw: — | Bukhari collection (auto-Sahih))_  
   Narrated Abu Huraira: Allah's Apostle has set forth an example for a miser and a charitable person by comparin…  
   score: 8.617

7. **bukhari:3755**  `Sahih` _(raw: — | Bukhari collection (auto-Sahih))_  
   Narrated Qais: Bilal said to Abu Bakr, "If you have bought me for yourself then keep me (for yourself), but if…  
   score: 8.572

8. **mishkat:5670**  `Uncategorized` _(raw: — | no grade data)_  
   He quoted the Prophet as stating that on the day of resurrection God will say to the inhabitant of hell who ha…  
   score: 8.486

9. **muslim:1548 e**  `Sahih` _(raw: — | Muslim collection (auto-Sahih))_  
   Rafi (Allah be pleased with him) reported that Zuhair b. Rafi (who was his uncle) came to me and said: Allah's…  
   score: 8.299

10. **bukhari:3791**  `Sahih` _(raw: — | Bukhari collection (auto-Sahih))_  
   Narrated Abu Humaid: The Prophet said, "The best of the Ansar families (homes) are the families (homes) of Ban…  
   score: 8.200


### `aisha`


#### hadithText (BM25)

_4,112 total matches_

1. **ibnmajah:1972**  `Sahih` _(raw: Sahih | graded: Sahih)_  
   'Urwah narrated from 'Aishah: that when Saudah bint Zam'ah grew old, she gave her day to 'Aishah, and the Mess…  
   score: 5.513

2. **bukhari:5212**  `Sahih` _(raw: — | Bukhari collection (auto-Sahih))_  
   Narrated `Aisha: Sauda bint Zam`a gave up her turn to me (`Aisha), and so the Prophet used to give me (`Aisha)…  
   score: 5.511

3. **muslim:2046 b**  `Sahih` _(raw: — | Muslim collection (auto-Sahih))_  
   'A'isha reported Allah's Messenger (may peace be upon him) as saying: 'A'isha a family which has no dates (in …  
   score: 5.503

4. **bulugh:1059**  `Uncategorized` _(raw: — | no grade data)_  
   Narrated 'Aishah (RA): Sauda (RA) daughter of Zam'ah gave away her day to 'Aishah (RA). So the Prophet (SAW) a…  
   score: 5.503

5. **nasai:3213**  `Sahih` _(raw: sahih | graded: sahih)_  
   Narrated 'Aishah: It was narrated from 'Aishah that the Messenger of Allah forbade celibacy.  
   score: 5.500

6. **muslim:2445**  `Sahih` _(raw: — | Muslim collection (auto-Sahih))_  
   'A'isha reported that when Allah's Messenger (may peace be upon him) set ont on a journey, he used to cast lot…  
   score: 5.495

7. **bukhari:5325, 5326**  `Sahih` _(raw: — | Bukhari collection (auto-Sahih))_  
   Narrated Qasim: Urwa said to Aisha, "Do you know so-and-so, the daughter of Al-Hakam? Her husband divorced her…  
   score: 5.493

8. **abudawud:1280**  `Da'if` ⚠️ _(raw: Da'if | graded: Da'if)_  
   Narrated Aisha, Ummul Mu'minin: Dhakwan, the client of Aisha, reported on the authority of Aisha: The Messenge…  
   score: 5.492

9. **ibnmajah:1469**  `Sahih` _(raw: Sahih | graded: Sahih)_  
   It was narrated from ‘Aishah that the Prophet (SAW) was shrouded in three white Yemeni cloths, among which the…  
   score: 5.492

10. **tirmidhi:3818**  `Hasan` _(raw: Hasan | graded: Hasan)_  
   Narrated 'Aishah, the Mother of the Believers: "The Prophet (SAW) wanted to wipe the running nose of Usamah." …  
   score: 5.489


#### englishMatn (BM25)

_447 total matches_

1. **bukhari:5325, 5326**  `Sahih` _(raw: — | Bukhari collection (auto-Sahih))_  
   Narrated Qasim: Urwa said to Aisha, "Do you know so-and-so, the daughter of Al-Hakam? Her husband divorced her…  
   score: 8.073

2. **bukhari:3217**  `Sahih` _(raw: — | Bukhari collection (auto-Sahih))_  
   Narrated Abu Salama: `Aisha said that the Prophet said to her "O `Aisha' This is Gabriel and he sends his (gre…  
   score: 7.996

3. **bukhari:5211**  `Sahih` _(raw: — | Bukhari collection (auto-Sahih))_  
   Narrated al-Qasim: Aisha said that whenever the Prophet intended to go on a journey, he drew lots among his wi…  
   score: 7.867

4. **bukhari:5212**  `Sahih` _(raw: — | Bukhari collection (auto-Sahih))_  
   Narrated `Aisha: Sauda bint Zam`a gave up her turn to me (`Aisha), and so the Prophet used to give me (`Aisha)…  
   score: 7.793

5. **bukhari:1446**  `Sahih` _(raw: — | Bukhari collection (auto-Sahih))_  
   Narrated Um 'Atiyya: A sheep was sent to me (Nusaiba Al-Ansariya) (in charity) and I sent some of it to `Aisha…  
   score: 7.750

6. **bukhari:321**  `Sahih` _(raw: — | Bukhari collection (auto-Sahih))_  
   Narrated Mu`adha: A woman asked `Aisha, "Should I offer the prayers that which I did not offer because of mens…  
   score: 7.656

7. **bukhari:6068**  `Sahih` _(raw: — | Bukhari collection (auto-Sahih))_  
   Narrated Al-Laith: `Aisha said "The Prophet entered upon me one day and said, 'O `Aisha! I do not think that s…  
   score: 7.616

8. **bukhari:6759**  `Sahih` _(raw: — | Bukhari collection (auto-Sahih))_  
   Narrated Ibn `Umar: When Aisha intended to buy Barira, she said to the Prophet, "Barira's masters stipulated t…  
   score: 7.514

9. **abudawud:1280**  `Da'if` ⚠️ _(raw: Da'if | graded: Da'if)_  
   Narrated Aisha, Ummul Mu'minin: Dhakwan, the client of Aisha, reported on the authority of Aisha: The Messenge…  
   score: 7.414

10. **bukhari:3768**  `Sahih` _(raw: — | Bukhari collection (auto-Sahih))_  
   Narrated Abu Salama: `Aisha said, "Once Allah's Apostle said (to me), 'O Aish (`Aisha)! This is Gabriel greeti…  
   score: 7.414


### `"actions are by intention"`


#### hadithText (BM25)

_844 total matches_

1. **forty:33**  `Uncategorized` _(raw: — | no grade data)_  
   Actions are through intentions.  
   score: 15.994

2. **riyadussalihin:11**  `Uncategorized` _(raw: — | no grade data)_  
   'Abdullah bin 'Abbas (May Allah be pleased with them) reported: Messenger of Allah (PBUH) said that Allah, the…  
   score: 12.074

3. **nasai:3794**  `Sahih` _(raw: sahih | graded: sahih)_  
   It was narrated from 'Umar bin Al-Khattab that the Prophet said: "Actions are but by intentions, and each pers…  
   score: 11.472

4. **nasai:3437**  `Sahih` _(raw: sahih | graded: sahih)_  
   It was narrated that 'Umar bin Al-Khattab, may Allah be pleased with him, said that the Messenger of Allah sai…  
   score: 11.472

5. **abudawud:2201**  `Sahih` _(raw: Sahih | graded: Sahih)_  
   ‘Umar bin Al Khattab reported the Apostle of Allaah(saws) as saying “Actions are to be judged only by intentio…  
   score: 11.472

6. **nasai:75**  `Sahih` _(raw: Sahih | graded: Sahih)_  
   It was narrated that 'Umar bin Al-Khattab (may Allah be pleased with him) said: "The Messenger of Allah said: …  
   score: 11.037

7. **ibnmajah:4227**  `Sahih` _(raw: Sahih | graded: Sahih)_  
   ‘Alqamah bin Waqqas (said) that he heard ‘Umar bin Khattab, when he was addressing the people, saying: “I hear…  
   score: 10.899

8. **muslim:1907 a**  `Sahih` _(raw: — | Muslim collection (auto-Sahih))_  
   It has been narrated on the authority of Umar b. al-Khattab that the Messenger of Allah (may peace be upon him…  
   score: 10.765

9. **bukhari:26**  `Sahih` _(raw: — | Bukhari collection (auto-Sahih))_  
   Narrated Abu Huraira: Allah's Apostle was asked, "What is the best deed?" He replied, "To believe in Allah and…  
   score: 10.505

10. **ahmad:300**  `Sahih` _(raw: Sahih (Darussalam) [ al Bukhari (1) and Muslim (1907) | graded: Sahih [ al Bukhari and Muslim)_  
   `Alqamah bin Waqqas al Laithi said that he heard `Umar bin al-Khattab addressing the people, and he said: I he…  
   score: 10.505


#### englishMatn (BM25)

_10,000 total matches_

1. **ibnmajah:4227**  `Sahih` _(raw: Sahih | graded: Sahih)_  
   ‘Alqamah bin Waqqas (said) that he heard ‘Umar bin Khattab, when he was addressing the people, saying: “I hear…  
   score: 15.588

2. **adab:8**  `Sahih` _(raw: Sahih | graded: Sahih)_  
   Taysala ibn Mayyas said, "I was with the Najadites [Kharijites] when I committed wrong actions which I suppose…  
   score: 13.306

3. **forty:33**  `Uncategorized` _(raw: — | no grade data)_  
   Actions are through intentions.  
   score: 12.312

4. **malik:1821**  `Uncategorized` _(raw: — | no grade data)_  
   Malik related to me that he heard that Isa ibn Maryam used to say, "Do not speak much without the mention of A…  
   score: 11.330

5. **bukhari:2783**  `Sahih` _(raw: — | Bukhari collection (auto-Sahih))_  
   Narrated Ibn `Abbas: Allah's Apostle said, "There is no Hijra (i.e. migration) (from Mecca to Medina) after th…  
   score: 11.301

6. **ibnmajah:2924**  `Uncategorized` _(raw: Da’if | graded: Da’if)_  
   It was narrated from Abu Bakr As-Siddiq that the Messenger of Allah (saw) was asked: “Which actions are best?”…  
   score: 11.286

7. **malik:508**  `Uncategorized` _(raw: — | no grade data)_  
   Yahya related to me from Malik that Zayd ibn Aslam used to say, "No-one makes a dua without one of three thing…  
   score: 11.117

8. **bulugh:1085**  `Uncategorized` _(raw: — | no grade data)_  
   Narrated 'Aishah (RA): The Prophet (SAW) said, "There are three people whose actions are not recorded, a sleep…  
   score: 10.833

9. **malik:61**  `Uncategorized` _(raw: — | no grade data)_  
   Yahya related to me from Malik from Zayd ibn Aslam from Ata ibn Yasar from Abdullah as-Sanabihi that the Messe…  
   score: 10.815

10. **abudawud:4398**  `Sahih` _(raw: Sahih | graded: Sahih)_  
   Narrated Aisha, Ummul Mu'minin: The Messenger of Allah (saws) said: There are three (persons) whose actions ar…  
   score: 10.234


### `actions are by intention`


#### hadithText (BM25)

_844 total matches_

1. **forty:33**  `Uncategorized` _(raw: — | no grade data)_  
   Actions are through intentions.  
   score: 15.994

2. **riyadussalihin:11**  `Uncategorized` _(raw: — | no grade data)_  
   'Abdullah bin 'Abbas (May Allah be pleased with them) reported: Messenger of Allah (PBUH) said that Allah, the…  
   score: 12.074

3. **nasai:3794**  `Sahih` _(raw: sahih | graded: sahih)_  
   It was narrated from 'Umar bin Al-Khattab that the Prophet said: "Actions are but by intentions, and each pers…  
   score: 11.472

4. **nasai:3437**  `Sahih` _(raw: sahih | graded: sahih)_  
   It was narrated that 'Umar bin Al-Khattab, may Allah be pleased with him, said that the Messenger of Allah sai…  
   score: 11.472

5. **abudawud:2201**  `Sahih` _(raw: Sahih | graded: Sahih)_  
   ‘Umar bin Al Khattab reported the Apostle of Allaah(saws) as saying “Actions are to be judged only by intentio…  
   score: 11.472

6. **nasai:75**  `Sahih` _(raw: Sahih | graded: Sahih)_  
   It was narrated that 'Umar bin Al-Khattab (may Allah be pleased with him) said: "The Messenger of Allah said: …  
   score: 11.037

7. **ibnmajah:4227**  `Sahih` _(raw: Sahih | graded: Sahih)_  
   ‘Alqamah bin Waqqas (said) that he heard ‘Umar bin Khattab, when he was addressing the people, saying: “I hear…  
   score: 10.899

8. **muslim:1907 a**  `Sahih` _(raw: — | Muslim collection (auto-Sahih))_  
   It has been narrated on the authority of Umar b. al-Khattab that the Messenger of Allah (may peace be upon him…  
   score: 10.765

9. **bukhari:26**  `Sahih` _(raw: — | Bukhari collection (auto-Sahih))_  
   Narrated Abu Huraira: Allah's Apostle was asked, "What is the best deed?" He replied, "To believe in Allah and…  
   score: 10.505

10. **ahmad:300**  `Sahih` _(raw: Sahih (Darussalam) [ al Bukhari (1) and Muslim (1907) | graded: Sahih [ al Bukhari and Muslim)_  
   `Alqamah bin Waqqas al Laithi said that he heard `Umar bin al-Khattab addressing the people, and he said: I he…  
   score: 10.505


#### englishMatn (BM25)

_10,000 total matches_

1. **ibnmajah:4227**  `Sahih` _(raw: Sahih | graded: Sahih)_  
   ‘Alqamah bin Waqqas (said) that he heard ‘Umar bin Khattab, when he was addressing the people, saying: “I hear…  
   score: 15.588

2. **adab:8**  `Sahih` _(raw: Sahih | graded: Sahih)_  
   Taysala ibn Mayyas said, "I was with the Najadites [Kharijites] when I committed wrong actions which I suppose…  
   score: 13.306

3. **forty:33**  `Uncategorized` _(raw: — | no grade data)_  
   Actions are through intentions.  
   score: 12.312

4. **malik:1821**  `Uncategorized` _(raw: — | no grade data)_  
   Malik related to me that he heard that Isa ibn Maryam used to say, "Do not speak much without the mention of A…  
   score: 11.330

5. **bukhari:2783**  `Sahih` _(raw: — | Bukhari collection (auto-Sahih))_  
   Narrated Ibn `Abbas: Allah's Apostle said, "There is no Hijra (i.e. migration) (from Mecca to Medina) after th…  
   score: 11.301

6. **ibnmajah:2924**  `Uncategorized` _(raw: Da’if | graded: Da’if)_  
   It was narrated from Abu Bakr As-Siddiq that the Messenger of Allah (saw) was asked: “Which actions are best?”…  
   score: 11.286

7. **malik:508**  `Uncategorized` _(raw: — | no grade data)_  
   Yahya related to me from Malik that Zayd ibn Aslam used to say, "No-one makes a dua without one of three thing…  
   score: 11.117

8. **bulugh:1085**  `Uncategorized` _(raw: — | no grade data)_  
   Narrated 'Aishah (RA): The Prophet (SAW) said, "There are three people whose actions are not recorded, a sleep…  
   score: 10.833

9. **malik:61**  `Uncategorized` _(raw: — | no grade data)_  
   Yahya related to me from Malik from Zayd ibn Aslam from Ata ibn Yasar from Abdullah as-Sanabihi that the Messe…  
   score: 10.815

10. **abudawud:4398**  `Sahih` _(raw: Sahih | graded: Sahih)_  
   Narrated Aisha, Ummul Mu'minin: The Messenger of Allah (saws) said: There are three (persons) whose actions ar…  
   score: 10.234


### `how to make wudu`


#### hadithText (BM25)

_5,796 total matches_

1. **ahmad:873**  `Sahih` _(raw: Sahih (Darussalam) [] | graded: Sahih [])_  
   It was narrated that Zirr bin Hubaish said: `Ali (رضي الله عنه) wiped his head in wudoo` until it was about to…  
   score: 11.599

2. **ibnmajah:284**  `Uncategorized` _(raw: — | no grade data)_  
   'Abdullah bin Mas'ud said: "It was said: 'O Messenger of Allah, how will you recognize those whom you have not…  
   score: 11.562

3. **mishkat:424**  `Uncategorized` _(raw: — | no grade data)_  
   ‘Uthman said that God’s messenger performed each detail of ablution three times and then said, “This is how I …  
   score: 11.482

4. **ahmad:1273**  `Hasan` _(raw: Hasan (Darussalam)] | graded: Hasan])_  
   It was narrated that Abu Hayyah bin Qais said: ’Ali (رضي الله عنه) did wudoo’, each part three times, then he …  
   score: 11.435

5. **riyadussalihin:1198**  `Uncategorized` _(raw: — | no grade data)_  
   'Aishah (may Allah be pleased with her) reported: We used to prepare for the Messenger of Allah (PBUH) a Miswa…  
   score: 11.413

6. **ahmad:554**  `Sahih` _(raw: Sahih Hadeeth, this isnad is Da'if because of a man and his  | graded: Sahih Hadeeth, this isnad is Da'if because of a man and his father from Ansar are unknown])_  
   It was narrated from one of the Ansar that his father said: I was standing with ‘Uthman bin `Affan (رضي الله ع…  
   score: 11.362

7. **ibnmajah:3179**  `Sahih` _(raw: Sahih | graded: Sahih)_  
   It was narrated from Abu Sa’eed Al-Khudri that the Messenger of Allah (saw) passed by a boy who was skinning a…  
   score: 11.286

8. **ahmad:436**  `Hasan` _(raw: Hasan (Darussalam) [] | graded: Hasan [])_  
   It was narrated that Muhammad bin ‘Abdullah bin Abi Maryam said: I entered upon Ibn Darah, the freed slave of …  
   score: 11.250

9. **nasai:140**  `Hasan` _(raw: Hasan | graded: Hasan)_  
   It was narrated from 'Amr bin Shu'aib, from his father, that his grandfather said: "A Bedouin came to the Prop…  
   score: 11.137

10. **tirmidhi:55**  `Da'if` ⚠️ _(raw: Da'if | graded: Da'if)_  
   Umar bin Al-Khattab narrated that : Allah's Messenger said: 'Whoever performs Wudu, making Wudu well, then say…  
   score: 11.116


#### englishMatn (BM25)

_10,000 total matches_

1. **nasai:140**  `Hasan` _(raw: Hasan | graded: Hasan)_  
   It was narrated from 'Amr bin Shu'aib, from his father, that his grandfather said: "A Bedouin came to the Prop…  
   score: 13.024

2. **riyadussalihin:1198**  `Uncategorized` _(raw: — | no grade data)_  
   'Aishah (may Allah be pleased with her) reported: We used to prepare for the Messenger of Allah (PBUH) a Miswa…  
   score: 11.802

3. **nasai:96**  `Sahih` _(raw: Sahih | graded: Sahih)_  
   It was narrated that Abu Hayyah - Ibn Qais - said: "I saw 'Ali perform Wudu'. He washed his hands until they l…  
   score: 11.351

4. **nasai:78**  `Sahih` _(raw: Sahih | graded: Sahih)_  
   It was narrated that Anas said: "Some of the Companions of the Prophet (PBUH) were looking for (water for) Wud…  
   score: 11.349

5. **nasai:89**  `Sahih` _(raw: Sahih | graded: Sahih)_  
   It was narrated from Salamah bin Qais that the Messenger of Allah (PBUH) said: "When you perform Wudu', sniff …  
   score: 11.226

6. **tirmidhi:27**  `Sahih` _(raw: Sahih | graded: Sahih)_  
   Salamah bin Qais narrated that : Allah's Messenger said: "When you perform Wudu then sniff water in the nose a…  
   score: 11.142

7. **nasai:88**  `Sahih` _(raw: Sahih | graded: Sahih)_  
   It was narrated from Abu Hurairah that the Messenger of Allah (PBUH) said: "Whoever performs Wudu' then let hi…  
   score: 11.142

8. **tirmidhi:3631**  `Sahih` _(raw: Sahih | graded: Sahih)_  
   Narrated Anas bin Malik: "I saw the Messenger of Allah (SAW) at the time when the 'Asr prayer had drawn near, …  
   score: 11.080

9. **ibnmajah:3179**  `Sahih` _(raw: Sahih | graded: Sahih)_  
   It was narrated from Abu Sa’eed Al-Khudri that the Messenger of Allah (saw) passed by a boy who was skinning a…  
   score: 10.707

10. **nasai:5730**  `Sahih` _(raw: Sahih | graded: Sahih)_  
   'Ata' said: "I heard Ibn 'Abbas say: 'By Allah, fire does not make anything permissible or forbidden.'" He sai…  
   score: 10.689


### `ramadan`


#### hadithText (BM25)

_728 total matches_

1. **tirmidhi:663**  `Da'if` ⚠️ _(raw: Da'if | graded: Da'if)_  
   Anas narrated that : the Prophet was asked which fast was most virtuous after Ramadan? He said: "Sha'ban in ho…  
   score: 9.053

2. **bukhari:2022**  `Sahih` _(raw: — | Bukhari collection (auto-Sahih))_  
   Narrated Ibn `Abbas: Allah's Apostle said, "The Night of Qadr is in the last ten nights of the month (Ramadan)…  
   score: 9.035

3. **ahmad:140**  `Uncategorized` _(raw: (A qawi hadeeth) | graded: )_  
   It was narrated that ‘Umar said: We went on a campaign with the Messenger of Allah ﷺ during Ramadan and the co…  
   score: 8.951

4. **bukhari:4502**  `Sahih` _(raw: — | Bukhari collection (auto-Sahih))_  
   Narrated `Aisha: The people used to fast on the day of 'Ashura' before fasting in Ramadan was prescribed but w…  
   score: 8.933

5. **bukhari:2020**  `Sahih` _(raw: — | Bukhari collection (auto-Sahih))_  
   Narrated `Aisha: Allah's Apostle used to practice I`tikaf in the last ten nights of Ramadan and used to say, "…  
   score: 8.933

6. **bukhari:6991**  `Sahih` _(raw: — | Bukhari collection (auto-Sahih))_  
   Narrated Ibn `Umar: Some people were shown the Night of Qadr as being in the last seven days (of the month of …  
   score: 8.933

7. **abudawud:1428**  `Da'if` ⚠️ _(raw: Da'if | graded: Da'if)_  
   Muhammad reported on the authority of some of his teachers that Ubayy b. Ka'b led them in prayer during Ramada…  
   score: 8.925

8. **tirmidhi:792**  `Sahih` _(raw: Sahih | graded: Sahih)_  
   Aishah narrated: "The Messenger of Allah would Yujawir (stay in I'tikaf) during the last ten (nights) of Ramad…  
   score: 8.916

9. **bukhari:2008**  `Sahih` _(raw: — | Bukhari collection (auto-Sahih))_  
   Narrated Abu Huraira: I heard Allah's Apostle saying regarding Ramadan, "Whoever prayed at night in it (the mo…  
   score: 8.890

10. **mishkat:564**  `Uncategorized` _(raw: — | no grade data)_  
   Abu Huraira reported God’s Messenger as saying, “The five [daily] prayers, Friday to Friday and Ramadan to Ram…  
   score: 8.881


#### englishMatn (BM25)

_715 total matches_

1. **tirmidhi:663**  `Da'if` ⚠️ _(raw: Da'if | graded: Da'if)_  
   Anas narrated that : the Prophet was asked which fast was most virtuous after Ramadan? He said: "Sha'ban in ho…  
   score: 7.389

2. **bukhari:2022**  `Sahih` _(raw: — | Bukhari collection (auto-Sahih))_  
   Narrated Ibn `Abbas: Allah's Apostle said, "The Night of Qadr is in the last ten nights of the month (Ramadan)…  
   score: 7.287

3. **ahmad:140**  `Uncategorized` _(raw: (A qawi hadeeth) | graded: )_  
   It was narrated that ‘Umar said: We went on a campaign with the Messenger of Allah ﷺ during Ramadan and the co…  
   score: 7.011

4. **mishkat:564**  `Uncategorized` _(raw: — | no grade data)_  
   Abu Huraira reported God’s Messenger as saying, “The five [daily] prayers, Friday to Friday and Ramadan to Ram…  
   score: 6.947

5. **tirmidhi:792**  `Sahih` _(raw: Sahih | graded: Sahih)_  
   Aishah narrated: "The Messenger of Allah would Yujawir (stay in I'tikaf) during the last ten (nights) of Ramad…  
   score: 6.884

6. **bukhari:6991**  `Sahih` _(raw: — | Bukhari collection (auto-Sahih))_  
   Narrated Ibn `Umar: Some people were shown the Night of Qadr as being in the last seven days (of the month of …  
   score: 6.884

7. **bukhari:2020**  `Sahih` _(raw: — | Bukhari collection (auto-Sahih))_  
   Narrated `Aisha: Allah's Apostle used to practice I`tikaf in the last ten nights of Ramadan and used to say, "…  
   score: 6.822

8. **muslim:1102 c**  `Sahih` _(raw: — | Muslim collection (auto-Sahih))_  
   A hadith like this has been transmitted by Ibn 'Umar (Allah be pleased with both of them), but he did not make…  
   score: 6.807

9. **abudawud:1428**  `Da'if` ⚠️ _(raw: Da'if | graded: Da'if)_  
   Muhammad reported on the authority of some of his teachers that Ubayy b. Ka'b led them in prayer during Ramada…  
   score: 6.791

10. **bukhari:2008**  `Sahih` _(raw: — | Bukhari collection (auto-Sahih))_  
   Narrated Abu Huraira: I heard Allah's Apostle saying regarding Ramadan, "Whoever prayed at night in it (the mo…  
   score: 6.761


### `music`


#### hadithText (BM25)

_14 total matches_

1. **abudawud:2556**  `Sahih` _(raw: Sahih | graded: Sahih)_  
   Abu Hurairah reported the Apostle of Allaah(saws) as saying “The bell is a wooden wind musical instrument of S…  
   score: 12.454

2. **muslim:2114**  `Sahih` _(raw: — | Muslim collection (auto-Sahih))_  
   Abu Huraira reported Allah's Messenger (may peace be upon him) as saying: The bell is the musical instrument o…  
   score: 12.350

3. **riyadussalihin:1691**  `Uncategorized` _(raw: — | no grade data)_  
   Abu Hurairah (May Allah be pleased with him) said: The Prophet (PBUH) said, "The bell is one of the musical in…  
   score: 12.148

4. **tirmidhi:2212**  `Da'if` ⚠️ _(raw: Da'if | graded: Da'if)_  
   'Imran bin Husain narrated that the Messenger of Allah(s.a.w) said: "In this Ummah there shall be collapsing o…  
   score: 10.740

5. **ibnmajah:4020**  `Hasan` _(raw: Hasan | graded: Hasan)_  
   It was narrated from Abu Malik Ash’ari that the Messenger of Allah (saw) said: “People among my nation will dr…  
   score: 10.438

6. **bukhari:952**  `Sahih` _(raw: — | Bukhari collection (auto-Sahih))_  
   Narrated Aisha: Abu Bakr came to my house while two small Ansari girls were singing beside me the stories of t…  
   score: 9.752

7. **bukhari:3931**  `Sahih` _(raw: — | Bukhari collection (auto-Sahih))_  
   Narrated Aisha: That once Abu Bakr came to her on the day of `Id-ul-Fitr or `Id ul Adha while the Prophet was …  
   score: 9.502

8. **bukhari:5590**  `Sahih` _(raw: — | Bukhari collection (auto-Sahih))_  
   Narrated Abu 'Amir or Abu Malik Al-Ash'ari: that he heard the Prophet saying, "From among my followers there w…  
   score: 8.520

9. **nasai:4135**  `Sahih` _(raw: Sahih | graded: Sahih)_  
   It was narrated that Al-Awza'i said: "Umar bin 'Abdul-'Aziz wrote a letter to 'Umar bin Al-Walid in which he s…  
   score: 7.970

10. **tirmidhi:2211**  `Da'if` ⚠️ _(raw: Da'if | graded: Da'if)_  
   Abu Hurairah narrated that the Messenger of Allah(s.a.w) said: "When Al-Fai' is distributed(preferentially), t…  
   score: 7.642


#### englishMatn (BM25)

_4 total matches_

1. **tirmidhi:2212**  `Da'if` ⚠️ _(raw: Da'if | graded: Da'if)_  
   'Imran bin Husain narrated that the Messenger of Allah(s.a.w) said: "In this Ummah there shall be collapsing o…  
   score: 11.643

2. **tirmidhi:2211**  `Da'if` ⚠️ _(raw: Da'if | graded: Da'if)_  
   Abu Hurairah narrated that the Messenger of Allah(s.a.w) said: "When Al-Fai' is distributed(preferentially), t…  
   score: 7.115

3. **tirmidhi:2210**  `Da'if` ⚠️ _(raw: Da'if | graded: Da'if)_  
   'Ali bin Abi Talib narrated that the Messenger of Allah(s.a.w) said: "When my Ummah does fifteen things, the a…  
   score: 7.115

4. **muslim:2448 a**  `Sahih` _(raw: — | Muslim collection (auto-Sahih))_  
   'A'isha reported that (one day) there sat together eleven women making an explicit promise amongst themselves …  
   score: 1.854


---
## Part 3 — Arabic Queries

Arabic queries route to `lexical_arabic` (BM25 on arabicText with Arabic analyzer).
All docs — both Arabic-only and bilingual — are searched.
Results show `[lang]` tag so you can see the mix.
Note: الرحمن / الرحمان / الرحمٰن are spelling variants — differences reveal analyzer normalization.


### `الرحمن`

_6,091 total matches, lang dist: en:10 ar:0_

1. **malik:1167** `[en]`  `Uncategorized` _(raw: — | no grade data)_  
   Yahya related to me from Malik from Abd ar-Rahman ibn al-Qasim from his father that A'isha, the wife of the Pr…  
   score: 4.254

2. **tirmidhi:3452** `[en]`  `Sahih` _(raw: Sahih | graded: Sahih)_  
   Mu`adh bin Jabal narrated : that one of the two men cursed the other next to the Prophet (saws), until anger c…  
   score: 4.155

3. **malik:1438** `[en]`  `Uncategorized` _(raw: — | no grade data)_  
   Malik related to me from Amr ibn Yahya al-Mazini that his father said, "There was a stream in my grand-father'…  
   score: 4.120

4. **abudawud:1995** `[en]`  `Sahih` _(raw: — | no grade data)_  
   Hafsah, daughter of AbdurRahman ibn AbuBakr, reported on the authority of her father: The Messenger of Allah (…  
   score: 4.111

5. **malik:1166** `[en]`  `Uncategorized` _(raw: — | no grade data)_  
   Yahya related to me from Malik from Abd ar-Rahman ibn al-Qasim from his father that A'isha, umm al-muminin, pr…  
   score: 4.111

6. **bukhari:7207** `[en]`  `Sahih` _(raw: — | Bukhari collection (auto-Sahih))_  
   Narrated Al-Miswar bin Makhrama: The group of people whom `Umar had selected as candidates for the Caliphate g…  
   score: 4.105

7. **tirmidhi:3747** `[en]`  `Sahih` _(raw: Sahih | graded: Sahih)_  
   Narrated 'Abdur-Rahman bin 'Awf: that the Messenger of Allah (SAW) said: "Abu Bakr is in Paradise, 'Umar is in…  
   score: 4.092

8. **malik:644** `[en]`  `Uncategorized` _(raw: — | no grade data)_  
   Yahya related to me from Malik from Sumayy, the mawla of Abu Bakr ibn Abd ar-Rahman ibn al-Harith ibn Hisham t…  
   score: 4.079

9. **malik:1200** `[en]`  `Uncategorized` _(raw: — | no grade data)_  
   Yahya related to me from Malik that he heard Rabia ibn Abi Abd ar-Rahman say, ''I heard that the wife of Abd a…  
   score: 4.075

10. **nasai:3268** `[en]`  `Sahih` _(raw: sahih | graded: sahih)_  
   It was narrated from Khansa' bint Khidham that her father married her off when she had been previously married…  
   score: 4.075


### `الرحمان`

_585 total matches, lang dist: en:10 ar:0_

1. **riyadussalihin:420** `[en]`  `Uncategorized` _(raw: — | no grade data)_  
   Abu Hurairah (May Allah be pleased with him) reported: Messenger of Allah (PBUH) said, "Allah has divided merc…  
   score: 8.751

2. **adab:1016** `[en]`  `Da'if` ⚠️ _(raw: — | no grade data)_  
   Salim, the mawla of 'Abdullah ibn 'Amr, said, "When Ibn 'Umar was greeted, he returned it with increase. I cam…  
   score: 8.520

3. **bukhari:6469** `[en]`  `Sahih` _(raw: — | Bukhari collection (auto-Sahih))_  
   Narrated Abu Huraira: I heard Allah's Apostle saying, Verily Allah created Mercy. The day He created it, He ma…  
   score: 8.459

4. **mishkat:2365, 2366** `[en]`  `Uncategorized` _(raw: — | no grade data)_  
   He reported God’s messenger as saying, “God has a hundred, mercies of which He has sent down one among jinn an…  
   score: 8.423

5. **mishkat:6134** `[en]`  `Uncategorized` _(raw: — | no grade data)_  
   He reported God's messenger as saying, "God show mercy to Aba Bakr! He gave me his daughter as wife, he convey…  
   score: 8.386

6. **muslim:2753 c** `[en]`  `Sahih` _(raw: — | Muslim collection (auto-Sahih))_  
   Salman reported that Allah's Messenger (may peace be upon him) said: Verily, Allah created, on the same very d…  
   score: 8.386

7. **ibnmajah:4293** `[en]`  `Sahih` _(raw: Sahih | graded: Sahih)_  
   It was narrated from Abu Hurairah that the Prophet (saw) said: “Allah has one hundred (degrees of) mercy, of w…  
   score: 8.103

8. **tirmidhi:3541** `[en]`  `Sahih` _(raw: Sahih | graded: Sahih)_  
   Abu Hurairah narrated that the Messenger of Allah (saws) said: “Allah created a hundred mercies, and He placed…  
   score: 8.080

9. **adab:987** `[en]`  `Sahih` _(raw: Sahih | graded: Sahih)_  
   'Umar said, "I was riding behind Abu Bakr and he passed by some people. He said, 'Peace be upon you.' They sai…  
   score: 8.080

10. **muslim:2752 c** `[en]`  `Sahih` _(raw: — | Muslim collection (auto-Sahih))_  
   Abu Huraira reported Allah's Messenger (may peace be upon him) as saying: There are one hundred (parts of) mer…  
   score: 8.080


### `الرحمٰن`

_0 total matches, lang dist: en:0 ar:0_

_No results — analyzer may not normalize this variant_

### `الرحمن قد اشتق من الرحم`

_10,000 total matches, lang dist: en:10 ar:0_

1. **bukhari:6469** `[en]`  `Sahih` _(raw: — | Bukhari collection (auto-Sahih))_  
   Narrated Abu Huraira: I heard Allah's Apostle saying, Verily Allah created Mercy. The day He created it, He ma…  
   score: 12.593

2. **abudawud:4542** `[en]`  `Hasan` _(raw: Hasan | graded: Hasan)_  
   Narrated 'Amr b. Suh'aib: On his father's authority, said that his grandfather reported that the value of the …  
   score: 12.543

3. **abudawud:5185** `[en]`  `Da'if` ⚠️ _(raw: Da'if in chain | graded: Da'if in chain)_  
   Narrated Qays ibn Sa'd: The Messenger of Allah (saws) came to visit us in our house, and said: Peace and Allah…  
   score: 12.392

4. **abudawud:5233** `[en]`  `Hasan` _(raw: Hasan | graded: Hasan)_  
   Narrated AbuAbdurRahman al-Fihri: I was present with the Messenger of Allah at the battle of Hunayn. We travel…  
   score: 12.307

5. **adab:381** `[en]`  `Hasan` _(raw: Hasan | graded: Hasan)_  
   Abu Umama that the Messenger of Allah, may Allah bless him and grant him peace, said, "Anyone who shows mercy,…  
   score: 12.245

6. **adab:397** `[en]`  `Sahih` _(raw: Sahih | graded: Sahih)_  
   'Awf ibn al-Harith ibn at-Tufayl, the nephew of 'A'isha, reported that 'A'isha was told that 'Abdullah ibn az-…  
   score: 12.171

7. **abudawud:2904** `[en]`  `Da'if` ⚠️ _(raw: Da'if | graded: Da'if)_  
   Narrated Buraydah ibn al-Hasib: A man of Khuza'ah died and his estate was brought to the Prophet (saws). He sa…  
   score: 12.155

8. **nasai:1324** `[en]`  `Sahih` _(raw: Sahih | graded: Sahih)_  
   It was narrated from 'Abdullah that: The Prophet (SAW) used to say salam to his right and to his left: As-sala…  
   score: 11.764

9. **riyadussalihin:1499** `[en]`  `Uncategorized` _(raw: — | no grade data)_  
   Abu Hurairah (May Allah be pleased with him) reported: The Messenger of Allah (PBUH), "The supplication of eve…  
   score: 11.635

10. **adab:35** `[en]`  `Da'if` ⚠️ _(raw: Da'if | graded: Da'if)_  
   Abu Usayd said, "We were with the Messenger of Allah, may Allah bless him and grant him peace, when a man aske…  
   score: 11.448


### Arabic variant analysis

Checking if the Arabic analyzer normalizes الرحمن / الرحمان / الرحمٰن to the same tokens:

| Query | Total hits |
|-------|-----------|
| `الرحمن` | 6,091 |
| `الرحمان` | 585 |
| `الرحمٰن` | 0 |
| `الرحمن قد اشتق من الرحم` | 10,000 |

If الرحمن and الرحمان return the same count, the analyzer normalizes alef variants.
If الرحمٰن (with superscript alef) returns fewer, it may not be normalized.


---
## Next: Semantic Model Comparison

Semantic models (small-model-eval index) require query embedding inside the container.
Run `small_model_comparison.py` to compare all 12 models × hadithText + englishMatn inputs.
Multilingual models (`multilingual-e5`, `english-openai-large`) will be a separate section.

