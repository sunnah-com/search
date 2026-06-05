# Focused Comparison

Queries: **"aisha"** · **"comparing yourself to others"**

## Models

| Model | Text embedded | Isnad stripped | Search method | Pool → shown |
|---|---|---|---|---|
| **BM25 Lexical** | `hadithText` full text | ✗ | BM25 full-text | 50 → 10 |
| **Mixedbread noisy** | `hadithText` full text | ✗ | Semantic HNSW (mxbai-embed-large) | 50 → 10 |
| **Mixedbread clean** | `englishMatn` clean matn | ✓ | Semantic HNSW (mxbai-embed-large) | 50 → 10 |
| **English OpenAI small** | `englishMatn` clean matn | ✓ | Centroid k=75 → HNSW | 50 → 10 |
| **English OpenAI large** | `englishMatn` clean matn | ✓ | Centroid k=150 → HNSW | 50 → 10 |
| **Arabic OpenAI small** | `arabicMatn` (44,896 translated) | ✓* | Centroid k=75 → HNSW | 50 → 10 |
| **Arabic OpenAI large** | `arabicMatn` (131,728 all) | ✓* | Centroid k=150 → HNSW | 50 → 10 |
| **E5 Multilingual** | `englishMatn` + `arabicMatn` shared | ✓ | Centroid k=75 → HNSW | 50 → 10 |

\* Arabic matn extraction: ~94% clean via HTML matn tags, ~5.7% have residual shortcode tags — re-embed fix pending.

*Chain-ref filter ON · Dedup ON · English text shown is `englishMatn` (isnad-stripped) for all models*

---

# Query: "aisha"

**Latency:** **BM25 Lexical (full text)** 67ms · **Mixedbread (noisy — full hadithText)** 900ms · **Mixedbread (clean matn)** 96ms · **English OpenAI small (clean matn)** 1031ms · **English OpenAI large (clean matn)** 403ms · **Arabic OpenAI (small)** 893ms · **Arabic OpenAI (large)** 233ms · **E5 Multilingual** 335ms  
**Arabic OpenAI (small) clusters:** [27, 74]  
**Arabic OpenAI (large) clusters:** [8, 60]  

## BM25 · Mixedbread

<table width="100%"><thead><tr>
<th width="4%">#</th>
<th width="32%">BM25 Lexical (full text)</th>
<th width="32%">Mixedbread (noisy — full hadithText)</th>
<th width="32%">Mixedbread (clean matn)</th>
</tr></thead><tbody>
<tr>
<td align="center" valign="top"><strong>1</strong></td>
<td valign="top"><strong>bukhari 5212</strong>&nbsp; 10.3074<br><br>Narrated `Aisha: Sauda bint Zam`a gave up her turn to me (`Aisha), and so the Prophet used to give me (`Aisha) both my day and the day of Sauda.<br><br><span dir="rtl" lang="ar"><big>يَقْسِمُ لِعَائِشَةَ بِيَوْمِهَا وَيَوْمِ سَوْدَةَ‏.‏</big></span></td>
<td valign="top"><strong>bukhari 2046</strong>&nbsp; 0.8533<br><br><em><small>⛓ Narrated `Urwa:</small></em><br><br>Aisha during her menses used to comb and oil the hair of the Prophet while he used to be in I`tikaf in the mosque. He would stretch out his head towards her while she was in her chamber.<br><br><span dir="rtl" lang="ar"><big>تُرَجِّلُ النَّبِيَّ صلى الله عليه وسلم وَهِيَ حَائِضٌ وَهْوَ مُعْتَكِفٌ فِي الْمَسْجِدِ وَهْىَ فِي حُجْرَتِهَا، يُنَاوِلُهَا رَأْسَهُ‏.‏</big></span></td>
<td valign="top"><strong>shamail 173</strong>&nbsp; 0.8569<br><br><em><small>⛓ Abu Musa al-Ash'ari said that the Prophet said (Allah bless him and give him peace):</small></em><br><br>“The superiority of 'Aisha over all other women is like the superiority of tharid [a dish of sopped bread, meat and broth] over all other food.”<br><br><span dir="rtl" lang="ar"><big>‏:‏ فَضْلُ عَائِشَةَ عَلَى النِّسَاءِ كَفَضْلِ الثَّرِيدِ عَلَى سَائِرِ الطَّعَامِ‏.‏</big></span></td>
</tr>
<tr>
<td align="center" valign="top"><strong>2</strong></td>
<td valign="top"><strong>bukhari 5325, 5326</strong>&nbsp; 10.2913<br><br>Narrated Qasim: Urwa said to Aisha, "Do you know so-and-so, the daughter of Al-Hakam? Her husband divorced her irrevocably and she left (her husband's house)." `Aisha said, "What a bad thing she has done!" 'Urwa said (to `Aisha), "Haven't you heard the statement of Fatima?" `Aisha replied, "It is not in her favor to mention." 'Urwa added, `Aisha reproached (Fatima) severely and said, "Fatima was in a lonely place, and she was prone to danger, so the Prophet allowed her (to go out of her husband's house).<br><br><span dir="rtl" lang="ar"><big>بِئْسَ مَا صَنَعَتْ‏.‏ قَالَ أَلَمْ تَسْمَعِي فِي قَوْلِ فَاطِمَةَ قَالَتْ أَمَا إِنَّهُ لَيْسَ لَهَا خَيْرٌ فِي ذِكْرِ هَذَا الْحَدِيثِ‏.‏</big></span></td>
<td valign="top"><strong>bukhari 3894</strong>&nbsp; 0.8518<br><br><em><small>⛓ Narrated Aisha:</small></em><br><br>The Prophet engaged me when I was a girl of six (years). We went to Medina and stayed at the home of Bani-al-Harith bin Khazraj. Then I got ill and my hair fell down. Later on my hair grew (again) and my mother, Um Ruman, came to me while I was playing in a swing with some of my girl friends. She called me, and I went to her, not knowing what she wanted to do to me. She caught me by the hand and made me stand at the door of the house. I was breathless then, and when my breathing became Allright, she took some water and rubbed my face and head with it. Then she took me into the house. There in <br><br><span dir="rtl" lang="ar"><big>تَزَوَّجَنِي النَّبِيُّ صلى الله عليه وسلم وَأَنَا بِنْتُ سِتِّ سِنِينَ، فَقَدِمْنَا [place]الْمَدِينَةَ [/place]فَنَزَلْنَا فِي بَنِي الْحَارِثِ بْنِ خَزْرَجٍ، فَوُعِكْتُ فَتَمَرَّقَ شَعَرِي فَوَفَى جُمَيْمَةً، فَأَتَتْنِي أُمِّي أُمُّ رُومَانَ وَإِنِّي لَفِي أُرْجُوحَةٍ وَمَعِي صَوَاحِبُ لِي، فَصَرَخَتْ بِي فَأَتَيْتُهَا لاَ أَدْرِي مَا تُرِيدُ بِي فَأَخَذَتْ بِيَدِي حَتَّى أَوْقَفَتْنِي عَلَى ب</big></span></td>
<td valign="top"><strong>bukhari 2046</strong>&nbsp; 0.8445<br><br><em><small>⛓ Narrated `Urwa:</small></em><br><br>Aisha during her menses used to comb and oil the hair of the Prophet while he used to be in I`tikaf in the mosque. He would stretch out his head towards her while she was in her chamber.<br><br><span dir="rtl" lang="ar"><big>تُرَجِّلُ النَّبِيَّ صلى الله عليه وسلم وَهِيَ حَائِضٌ وَهْوَ مُعْتَكِفٌ فِي الْمَسْجِدِ وَهْىَ فِي حُجْرَتِهَا، يُنَاوِلُهَا رَأْسَهُ‏.‏</big></span></td>
</tr>
<tr>
<td align="center" valign="top"><strong>3</strong></td>
<td valign="top"><strong>bukhari 6201</strong>&nbsp; 10.2869<br><br>Narrated `Aisha: (the wife the Prophet) Allah's Apostle said, "O Aisha! This is Gabriel sending his greetings to you." I said, "Peace, and Allah's Mercy be on him." `Aisha added: The Prophet used to see things which we used not to see.<br><br><span dir="rtl" lang="ar"><big>يَا عَائِشَ هَذَا [name role="angel"]جِبْرِيلُ [/name]يُقْرِئُكِ السَّلاَمَ ‏"‏‏.‏ قُلْتُ وَعَلَيْهِ السَّلاَمُ وَرَحْمَةُ اللَّهِ‏.‏ قَالَتْ وَهْوَ يَرَى مَا لاَ نَرَى</big></span></td>
<td valign="top"><strong>bukhari 5959</strong>&nbsp; 0.8461<br><br><em><small>⛓ Narrated Anas:</small></em><br><br>Aisha had a thick curtain (having pictures on it) and she screened the side of her i house with it. The Prophet said to her, "Remove it from my sight, for its pictures are still coming to my mind in my prayers."<br><br><span dir="rtl" lang="ar"><big>أَمِيطِي عَنِّي، فَإِنَّهُ لاَ تَزَالُ تَصَاوِيرُهُ تَعْرِضُ لِي فِي صَلاَتِي ‏"</big></span></td>
<td valign="top"><strong>nasai 773</strong>&nbsp; 0.8384<br><br><em><small>⛓ Khilas bin 'Amr said:</small></em><br><br>"I heard Aisha (ra) say: 'The Messenger of Allah (saws), Abii Al-Qbim, and I were beneath a single blanket, and I was menstruating. If something got on him from me, he would wash whatever had got on him and he did not wash anywhere else, and he prayed in it then came back to me.And if anything got on him from me,he would do exactly the same and he did not wash anywhere else."'<br><br><span dir="rtl" lang="ar"><big>عَائِشَةَ، تَقُولُ كُنْتُ أَنَا وَرَسُولُ اللَّهِ، صلى الله عليه وسلم أَبُو الْقَاسِمِ فِي الشِّعَارِ الْوَاحِدِ وَأَنَا حَائِضٌ، طَامِثٌ فَإِنْ أَصَابَهُ مِنِّي شَىْءٌ غَسَلَ مَا أَصَابَهُ لَمْ يَعْدُهُ إِلَى غَيْرِهِ وَصَلَّى فِيهِ ثُمَّ يَعُودُ مَعِي فَإِنْ أَصَابَهُ مِنِّي شَىْءٌ فَعَلَ مِثْلَ ذَلِكَ لَمْ يَعْدُهُ إِلَى غَيْرِهِ ‏.‏</big></span></td>
</tr>
<tr>
<td align="center" valign="top"><strong>4</strong></td>
<td valign="top"><strong>bukhari 5211</strong>&nbsp; 10.2778<br><br>Narrated al-Qasim: Aisha said that whenever the Prophet intended to go on a journey, he drew lots among his wives (so as to take one of them along with him). During one of his journeys the lot fell on `Aisha and Hafsa. When night fell the Prophet would ride beside `Aisha and talk with her. One night Hafsa said to `Aisha, "Won't you ride my camel tonight and I ride yours, so that you may see (me) and I see (you) (in new situation)?" `Aisha said, "Yes, (I agree.)" So `Aisha rode, and then the Prophet came towards `Aisha's camel on which Hafsa was riding. He greeted Hafsa and then proceeded (besi<br><br><span dir="rtl" lang="ar"><big>أَقْرَعَ بَيْنَ نِسَائِهِ، فَطَارَتِ الْقُرْعَةُ لِعَائِشَةَ وَحَفْصَةَ، وَكَانَ النَّبِيُّ صلى الله عليه وسلم إِذَا كَانَ بِاللَّيْلِ سَارَ مَعَ عَائِشَةَ يَتَحَدَّثُ، فَقَالَتْ حَفْصَةُ أَلاَ تَرْكَبِينَ اللَّيْلَةَ بَعِيرِي وَأَرْكَبُ بَعِيرَكِ تَنْظُرِينَ وَأَنْظُرُ، فَقَالَتْ بَلَى فَرَكِبَتْ فَجَاءَ النَّبِيُّ صلى الله عليه وسلم إِلَى جَمَلِ عَائِشَةَ وَعَلَيْهِ حَفْصَةُ فَسَلَّمَ عَلَيْهَا </big></span></td>
<td valign="top"><strong>bukhari 1151</strong>&nbsp; 0.8434<br><br><em><small>⛓ Narrated 'Aisha:</small></em><br><br>A woman from the tribe of Bani Asad was sitting with me and Allah's Apostle (p.b.u.h) came to my house and said, "Who is this?" I said, "(She is) So and so. She does not sleep at night because she is engaged in prayer." The Prophet said disapprovingly: Do (good) deeds which is within your capacity as Allah never gets tired of giving rewards till you get tired of doing good deeds."<br><br><span dir="rtl" lang="ar"><big>مَهْ عَلَيْكُمْ مَا تُطِيقُونَ مِنَ الأَعْمَالِ، فَإِنَّ اللَّهَ لاَ يَمَلُّ حَتَّى تَمَلُّوا ‏"</big></span></td>
<td valign="top"><strong>bukhari 5818</strong>&nbsp; 0.8382<br><br><em><small>⛓ Narrated Abu Burda:</small></em><br><br>Aisha brought out to us a Kisa and an Izar and said, "The Prophet died while wearing these two." (Kisa, a square black piece of woolen cloth. Izar, a sheet cloth garment covering the lower half of the body).<br><br><span dir="rtl" lang="ar"><big>قُبِضَ رُوحُ النَّبِيِّ صلى الله عليه وسلم فِي هَذَيْنِ‏.‏</big></span></td>
</tr>
<tr>
<td align="center" valign="top"><strong>5</strong></td>
<td valign="top"><strong>bukhari 3217</strong>&nbsp; 10.2717<br><br>Narrated Abu Salama: `Aisha said that the Prophet said to her "O `Aisha' This is Gabriel and he sends his (greetings) salutations to you." `Aisha said, "Salutations (Greetings) to him, and Allah's Mercy and Blessings be on him," and addressing the Prophet she said, "You see what I don't see."<br><br><span dir="rtl" lang="ar"><big>يَا عَائِشَةُ، هَذَا [name role="angel"]جِبْرِيلُ [/name]يَقْرَأُ عَلَيْكِ السَّلاَمَ ‏"‏‏.‏ فَقَالَتْ وَعَلَيْهِ السَّلاَمُ وَرَحْمَةُ اللَّهِ وَبَرَكَاتُهُ‏.‏ تَرَى مَا لاَ أَرَى‏.‏ تُرِيدُ النَّبِيَّ صلى الله عليه وسلم‏.‏</big></span></td>
<td valign="top"><strong>abudawud 288</strong>&nbsp; 0.8402<br><br><em><small>⛓ 'Aishah, wife of Prophet (saws), said:</small></em><br><br>Umm Habibah, daughter of Jahsh, sister-in-law of Messenger of Allah (saws) and wife of 'Abd al-Rahman b. 'Awf, had a flow of blood for seven years. She asked the Messenger of Allah (saws) about it. The Messenger of Allah (saws) said: This is not menstruation but only vein; so you should take a bath and pray. 'Aishah said: She used to take bath in a wash-tub in the apartment of her sister Zainab daughter of Jahsh ; the redness of (her) blood dominated the water.<br><br><span dir="rtl" lang="ar"><big>رَسُولُ اللَّهِ صلى الله عليه وسلم ‏"‏ إِنَّ هَذِهِ لَيْسَتْ بِالْحَيْضَةِ وَلَكِنْ هَذَا عِرْقٌ فَاغْتَسِلِي وَصَلِّي ‏"‏ ‏.‏ قَالَتْ عَائِشَةُ فَكَانَتْ تَغْتَسِلُ فِي مِرْكَنٍ فِي حُجْرَةِ أُخْتِهَا زَيْنَبَ بِنْتِ جَحْشٍ حَتَّى تَعْلُوَ حُمْرَةُ الدَّمِ الْمَاءَ ‏.‏</big></span></td>
<td valign="top"><strong>abudawud 269</strong>&nbsp; 0.8375<br><br><em><small>⛓ Narrated Aisha, Ummul Mu'minin:</small></em><br><br>Khallas al-Hujari reported: Aisha said: I and the Messenger of Allah (saws) used to pass night in one (piece of) cloth (on me) while I menstruated profusely. If anything from me (i.e. blood) smeared him (i.e. his body), he would wash that spot and would not exceed it (in washing), then he would offer prayer with it.<br><br><span dir="rtl" lang="ar"><big>عَائِشَةَ، - رضى الله عنها - تَقُولُ كُنْتُ أَنَا وَرَسُولُ اللَّهِ، صلى الله عليه وسلم نَبِيتُ فِي الشِّعَارِ الْوَاحِدِ وَأَنَا حَائِضٌ طَامِثٌ فَإِنْ أَصَابَهُ مِنِّي شَىْءٌ غَسَلَ مَكَانَهُ وَلَمْ يَعْدُهُ ثُمَّ صَلَّى فِيهِ وَإِنْ أَصَابَ - تَعْنِي ثَوْبَهُ - مِنْهُ شَىْءٌ غَسَلَ مَكَانَهُ وَلَمْ يَعْدُهُ ثُمَّ صَلَّى فِيهِ ‏.‏</big></span></td>
</tr>
<tr>
<td align="center" valign="top"><strong>6</strong></td>
<td valign="top"><strong>bukhari 1446</strong>&nbsp; 10.2666<br><br>Narrated Um 'Atiyya: A sheep was sent to me (Nusaiba Al-Ansariya) (in charity) and I sent some of it to `Aisha. The Prophet asked `Aisha for something to eat. `Aisha replied that there was nothing except what Nusaiba Al-Ansariya had sent of that sheep. The Prophet said to her, "Bring it as it has reached its place."<br><br><span dir="rtl" lang="ar"><big>عِنْدَكُمْ شَىْءٌ ‏"‏‏.‏ فَقُلْتُ لاَ إِلاَّ مَا أَرْسَلَتْ بِهِ نُسَيْبَةُ مِنْ تِلْكَ الشَّاةِ فَقَالَ ‏"‏ هَاتِ فَقَدْ بَلَغَتْ مَحِلَّهَا ‏"</big></span></td>
<td valign="top"><strong>ibnmajah 630</strong>&nbsp; 0.8387<br><br><em><small>⛓ It was narrated that 'Aisha the wife of the Prophet said:</small></em><br><br>"One of us used to menstruate, then rub the blood off her garment when she became pure again, and wash it, and sprinkle water over the rest of the garment, then perform prayer in it."<br><br><span dir="rtl" lang="ar"><big>تْ إِنْ كَانَتْ إِحْدَانَا لَتَحِيضُ ثُمَّ تَقْتَنِصُ الدَّمَ مِنْ ثَوْبِهَا عِنْدَ طُهْرِهَا فَتَغْسِلُهُ وَتَنْضِحُ عَلَى سَائِرِهِ ثُمَّ تُصَلِّي فِيهِ ‏.‏</big></span></td>
<td valign="top"><strong>bukhari 3108</strong>&nbsp; 0.8363<br><br><em><small>⛓ Narrated Abu Burda:</small></em><br><br>`Aisha brought out to us a patched wool Len garment, and she said, "(It chanced that) the soul of Allah's Apostle was taken away while he was wearing this." Abu-Burda added, "Aisha brought out to us a thick waist sheet like the ones made by the Yemenites, and also a garment of the type called Al- Mulabbada."<br><br><span dir="rtl" lang="ar"><big>ـ كِسَاءً مُلَبَّدًا وَقَالَتْ فِي هَذَا نُزِعَ رُوحُ النَّبِيِّ صلى الله عليه وسلم‏.‏ وَزَادَ سُلَيْمَانُ عَنْ حُمَيْدٍ عَنْ أَبِي بُرْدَةَ قَالَ أَخْرَجَتْ إِلَيْنَا عَائِشَةُ إِزَارًا غَلِيظًا مِمَّا يُصْنَعُ [place]بِالْيَمَنِ، [/place]وَكِسَاءً مِنْ هَذِهِ الَّتِي يَدْعُونَهَا الْمُلَبَّدَةَ‏.‏</big></span></td>
</tr>
<tr>
<td align="center" valign="top"><strong>7</strong></td>
<td valign="top"><strong>bukhari 2647</strong>&nbsp; 10.2616<br><br>Narrated Aisha: Once the Prophet came to me while a man was in my house. He said, "O `Aisha! Who is this (man)?" I replied, "My foster brothers" He said, "O `Aisha! Be sure about your foster brothers, as fostership is only valid if it takes place in the suckling period (before two years of age).<br><br><span dir="rtl" lang="ar"><big>انْظُرْنَ مَنْ إِخْوَانُكُنَّ، فَإِنَّمَا الرَّضَاعَةُ مِنَ الْمَجَاعَةِ ‏"</big></span></td>
<td valign="top"><strong>abudawud 269</strong>&nbsp; 0.8385<br><br><em><small>⛓ Narrated Aisha, Ummul Mu'minin:</small></em><br><br>Khallas al-Hujari reported: Aisha said: I and the Messenger of Allah (saws) used to pass night in one (piece of) cloth (on me) while I menstruated profusely. If anything from me (i.e. blood) smeared him (i.e. his body), he would wash that spot and would not exceed it (in washing), then he would offer prayer with it.<br><br><span dir="rtl" lang="ar"><big>عَائِشَةَ، - رضى الله عنها - تَقُولُ كُنْتُ أَنَا وَرَسُولُ اللَّهِ، صلى الله عليه وسلم نَبِيتُ فِي الشِّعَارِ الْوَاحِدِ وَأَنَا حَائِضٌ طَامِثٌ فَإِنْ أَصَابَهُ مِنِّي شَىْءٌ غَسَلَ مَكَانَهُ وَلَمْ يَعْدُهُ ثُمَّ صَلَّى فِيهِ وَإِنْ أَصَابَ - تَعْنِي ثَوْبَهُ - مِنْهُ شَىْءٌ غَسَلَ مَكَانَهُ وَلَمْ يَعْدُهُ ثُمَّ صَلَّى فِيهِ ‏.‏</big></span></td>
<td valign="top"><strong>bukhari 6757</strong>&nbsp; 0.8362 <small>· dup:20400</small><br><br><em><small>⛓ Narrated Ibn `Umar:</small></em><br><br>That Aisha, the mother of the Believers, intended to buy a slave girl in order to manumit her. The slave girl's master said, "We are ready to sell her to you on the condition that her Wala should be for us." Aisha mentioned that to Allah's Apostle who said, "This (condition) should not prevent you from buying her, for the Wala is for the one who manumits (the slave)."<br><br><span dir="rtl" lang="ar"><big>الْوَلاَءُ لِمَنْ أَعْتَقَ ‏"</big></span></td>
</tr>
<tr>
<td align="center" valign="top"><strong>8</strong></td>
<td valign="top"><strong>bukhari 2717</strong>&nbsp; 10.2497<br><br>Narrated `Urwa: Aisha told me that Barirah came to seek her help in writing for emancipation and at that time she had not paid any part of her price. `Aisha said to her, "Go to your masters and if they agree that I will pay your price (and free you) on condition that your Wala' will be for me, I will pay the money." Barirah told her masters about that, but they refused, and said, "If `Aisha wants to do a favor she could, but your Wala will be for us." Aisha informed Allah's Apostle of that and he said to her, "Buy and manumit Barirah as the Wala' will go to the manumitted."<br><br><span dir="rtl" lang="ar"><big>‏ ابْتَاعِي فَأَعْتِقِي، فَإِنَّمَا الْوَلاَءُ لِمَنْ أَعْتَقَ ‏"</big></span></td>
<td valign="top"><strong>bukhari 4723</strong>&nbsp; 0.8376<br><br><em><small>⛓ Narrated Aisha:</small></em><br><br>The (above) verse was revealed in connection with the invocations.<br><br><span dir="rtl" lang="ar"><big>أُنْزِلَ ذَلِكَ فِي الدُّعَاءِ‏.‏</big></span></td>
<td valign="top"><strong>tirmidhi 3889</strong>&nbsp; 0.8338<br><br><em><small>⛓ Narrated 'Ammar bin Yasir:</small></em><br><br>"She is his wife in the world and in the Hereafter." - meaning: 'Aishah [may Allah be pleased with her].<br><br><span dir="rtl" lang="ar"><big>هِيَ زَوْجَتُهُ فِي الدُّنْيَا وَالآخِرَةِ ‏.‏ يَعْنِي عَائِشَةَ رضى الله عنها ‏.‏ هَذَا حَدِيثٌ حَسَنٌ صَحِيحٌ ‏.‏ وَفِي الْبَابِ عَنْ عَلِيِّ ‏.‏</big></span></td>
</tr>
<tr>
<td align="center" valign="top"><strong>9</strong></td>
<td valign="top"><strong>bukhari 321</strong>&nbsp; 10.2465<br><br>Narrated Mu`adha: A woman asked `Aisha, "Should I offer the prayers that which I did not offer because of menses" `Aisha said, "Are you from the Huraura' (a town in Iraq?) We were with the Prophet and used to get our periods but he never ordered us to offer them (the Prayers missed during menses)." `Aisha perhaps said, "We did not offer them."<br><br><span dir="rtl" lang="ar"><big>كُنَّا نَحِيضُ مَعَ النَّبِيِّ صلى الله عليه وسلم فَلاَ يَأْمُرُنَا بِهِ‏.‏ أَوْ قَالَتْ فَلاَ نَفْعَلُهُ‏.‏</big></span></td>
<td valign="top"><strong>bukhari 277</strong>&nbsp; 0.8360<br><br><em><small>⛓ Narrated Aisha:</small></em><br><br>Whenever any one of us was Junub, she poured water over her head thrice with both her hands and then rubbed the right side of her head with one hand and rubbed the left side of the head with the other hand.<br><br><span dir="rtl" lang="ar"><big>إِذَا أَصَابَتْ إِحْدَانَا جَنَابَةٌ، أَخَذَتْ بِيَدَيْهَا ثَلاَثًا فَوْقَ رَأْسِهَا، ثُمَّ تَأْخُذُ بِيَدِهَا عَلَى شِقِّهَا الأَيْمَنِ، وَبِيَدِهَا الأُخْرَى عَلَى شِقِّهَا الأَيْسَرِ‏.‏</big></span></td>
<td valign="top"><strong>ibnmajah 1877</strong>&nbsp; 0.8328<br><br><em><small>⛓ It was narrated that: Abdullah said:</small></em><br><br>“The Prophet married Aishah when she was seven years old, and consummated the marriage with her when she was nine, and he passed away when she was eighteen.”<br><br><span dir="rtl" lang="ar"><big>تَزَوَّجَ النَّبِيُّ ـ صلى الله عليه وسلم ـ عَائِشَةَ وَهِيَ بِنْتُ سَبْعٍ وَبَنَى بِهَا وَهِيَ بِنْتُ تِسْعٍ وَتُوُفِّيَ عَنْهَا وَهِيَ بِنْتُ ثَمَانِي عَشْرَةَ سَنَةً ‏.‏</big></span></td>
</tr>
<tr>
<td align="center" valign="top"><strong>10</strong></td>
<td valign="top"><strong>bukhari 2565</strong>&nbsp; 10.2430<br><br>Narrated `Abdul Wahid bin Aiman: I went to `Aisha and said, "I was the slave of `Utba bin Abu Lahab. "Utba died and his sons became my masters who sold me to Ibn Abu `Amr who manumitted me. The sons of `Utba stipulated that my Wala' should be for them." `Aisha said, "Barirah came to me and she was given the writing of emancipation by her masters and she asked me to buy and manumit her. I agreed to it, but Barirah told me that her masters would not sell her unless her Wala' was for them." `Aisha said, "I am not in need of that." When the Prophet heard that, or he was told about it, he asked `Ai<br><br><span dir="rtl" lang="ar"><big>الْوَلاَءُ لِمَنْ أَعْتَقَ، وَإِنِ اشْتَرَطُوا مِائَةَ شَرْطٍ ‏"</big></span></td>
<td valign="top"><strong>bukhari 2661</strong>&nbsp; 0.8355<br><br><em><small>⛓ Narrated Aisha:</small></em><br><br>(the wife of the Prophet) "Whenever Allah's Apostle intended to go on a journey, he would draw lots amongst his wives and would take with him the one upon whom the lot fell. During a Ghazwa of his, he drew lots amongst us and the lot fell upon me, and I proceeded with him after Allah had decreed the use of the veil by women. I was carried in a Howdah (on the camel) and dismounted while still in it. When Allah's Apostle was through with his Ghazwa and returned home, and we approached the city of Medina, Allah's Apostle ordered us to proceed at night. When the order of setting off was given, I w<br><br><span dir="rtl" lang="ar"><big>إِذَا أَرَادَ أَنْ يَخْرُجَ سَفَرًا أَقْرَعَ بَيْنَ أَزْوَاجِهِ، فَأَيَّتُهُنَّ خَرَجَ سَهْمُهَا خَرَجَ بِهَا مَعَهُ، فَأَقْرَعَ بَيْنَنَا فِي غَزَاةٍ غَزَاهَا فَخَرَجَ سَهْمِي، فَخَرَجْتُ مَعَهُ بَعْدَ مَا أُنْزِلَ الْحِجَابُ، فَأَنَا أُحْمَلُ فِي هَوْدَجٍ وَأُنْزَلُ فِيهِ، فَسِرْنَا حَتَّى إِذَا فَرَغَ رَسُولُ اللَّهِ صلى الله عليه وسلم مِنْ غَزْوَتِهِ تِلْكَ، وَقَفَلَ وَدَنَوْنَا مِنَ [place]ال</big></span></td>
<td valign="top"><strong>ibnmajah 626</strong>&nbsp; 0.8313<br><br><em><small>⛓ It was narrated from 'Urwah bin Zubair and 'Amrah bint 'Abdur-Rahman that :</small></em><br><br>'Aishah the wife of the Prophet said: "Umm Habibah Jahsh experienced prolonged non-menstrual bleeding for seven years when she was married to 'Abdur-Rahman bin 'Awf. She complained about that to the Prophet and the Prophet said: 'That is not menstruation, rather it is a vein, so when the time of your period comes, leave the prayer, and when it is over, take a bath and perform prayer.'" 'Aishah said: "She used to bathe for every prayer and then perform the prayer. She used to sit in a washtub belonging to her sister Zainab bint Jahsh and the blood would turn the water red."<br><br><span dir="rtl" lang="ar"><big>النَّبِيُّ ـ صلى الله عليه وسلم ـ ‏"‏ إِنَّ هَذِهِ لَيْسَتْ بِالْحَيْضَةِ وَإِنَّمَا هُوَ عِرْقٌ فَإِذَا أَقْبَلَتِ الْحَيْضَةُ فَدَعِي الصَّلاَةَ وَإِذَا أَدْبَرَتْ فَاغْتَسِلِي وَصَلِّي ‏"‏ ‏.‏ قَالَتْ عَائِشَةُ فَكَانَتْ تَغْتَسِلُ لِكُلِّ صَلاَةٍ ثُمَّ تُصَلِّي وَكَانَتْ تَقْعُدُ فِي مِرْكَنٍ لأُخْتِهَا زَيْنَبَ بِنْتِ جَحْشٍ حَتَّى إِنَّ حُمْرَةَ الدَّمِ لَتَعْلُو الْمَاءَ ‏.‏</big></span></td>
</tr>
</tbody></table>

## English OpenAI

<table width="100%"><thead><tr>
<th width="4%">#</th>
<th width="48%">English OpenAI small (clean matn)</th>
<th width="48%">English OpenAI large (clean matn)</th>
</tr></thead><tbody>
<tr>
<td align="center" valign="top"><strong>1</strong></td>
<td valign="top"><strong>bukhari 275</strong>&nbsp; 0.7867<br><br>Narrated Um Ruman: Aisha's mother, When `Aisha was accused, she fell down Unconscious.<br><br><span dir="rtl" lang="ar"><big>فَخَرَجَ إِلَيْنَا رَسُولُ اللَّهِ صلى الله عليه وسلم فَلَمَّا قَامَ فِي مُصَلاَّهُ ذَكَرَ أَنَّهُ جُنُبٌ فَقَالَ لَنَا ‏:‏ ‏"‏ مَكَانَكُمْ ‏"‏‏.‏ ثُمَّ رَجَعَ فَاغْتَسَلَ، ثُمَّ خَرَجَ إِلَيْنَا وَرَأْسُهُ يَقْطُرُ، فَكَبَّرَ فَصَلَّيْنَا مَعَهُ‏.‏</big></span></td>
<td valign="top"><strong>bukhari 447</strong>&nbsp; 0.6050 <small>· dup:65320</small><br><br><span dir="rtl" lang="ar"><big>وَيْحَ عَمَّارٍ تَقْتُلُهُ الْفِئَةُ الْبَاغِيَةُ، يَدْعُوهُمْ إِلَى الْجَنَّةِ، وَيَدْعُونَهُ إِلَى النَّارِ ‏"</big></span></td>
</tr>
<tr>
<td align="center" valign="top"><strong>2</strong></td>
<td valign="top"><strong>abudawud 2909</strong>&nbsp; 0.7826<br><br>Narrated Ibn 'Umar: 'Aishah, mother of believers (ra), intended to buy a slave-girl to set her free. Her people said: We shall sell her to you on one condition that we shall inherit from her. 'Aishah mentioned it to the Messenger of Allah (saws). He said: That should not prevent you, for the right of inheritance belongs to the one who has set a person free.<br><br><span dir="rtl" lang="ar"><big>‏"‏ لاَ يَرِثُ الْمُسْلِمُ الْكَافِرَ وَلاَ الْكَافِرُ الْمُسْلِمَ ‏"‏ ‏.‏</big></span></td>
<td valign="top"><strong>bukhari 368</strong>&nbsp; 0.6050<br><br><span dir="rtl" lang="ar"><big>عَنْ بَيْعَتَيْنِ عَنِ اللِّمَاسِ وَالنِّبَاذِ، وَأَنْ يَشْتَمِلَ الصَّمَّاءَ، وَأَنْ يَحْتَبِيَ الرَّجُلُ فِي ثَوْبٍ وَاحِدٍ‏.‏</big></span></td>
</tr>
<tr>
<td align="center" valign="top"><strong>3</strong></td>
<td valign="top"><strong>bukhari 842</strong>&nbsp; 0.7819<br><br>Narrated Anas: Aisha had a thick curtain (having pictures on it) and she screened the side of her i house with it. The Prophet said to her, "Remove it from my sight, for its pictures are still coming to my mind in my prayers."<br><br><span dir="rtl" lang="ar"><big>انْقِضَاءَ صَلاَةِ النَّبِيِّ صلى الله عليه وسلم بِالتَّكْبِيرِ‏.‏</big></span></td>
<td valign="top"><strong>abudawud 4495</strong>&nbsp; 0.6050<br><br><span dir="rtl" lang="ar"><big>لأَبِي ‏"‏ ابْنُكَ هَذَا ‏"‏ ‏.‏ قَالَ إِي وَرَبِّ الْكَعْبَةِ قَالَ ‏"‏ حَقًّا ‏"‏ ‏.‏ قَالَ أَشْهَدُ بِهِ ‏.‏ قَالَ فَتَبَسَّمَ رَسُولُ اللَّهِ صلى الله عليه وسلم ضَاحِكًا مِنْ ثَبْتِ شَبَهِي فِي أَبِي وَمِنْ حَلْفِ أَبِي عَلَىَّ ‏.‏ ثُمَّ قَالَ ‏"‏ أَمَا إِنَّهُ لاَ يَجْنِي عَلَيْكَ وَلاَ تَجْنِي عَلَيْهِ ‏"‏ ‏.‏ وَقَرَأَ رَسُولُ اللَّهِ صلى الله عليه وسلم ‏ {‏ وَلاَ تَزِرُ وَازِرَةٌ وِزْرَ أُخ</big></span></td>
</tr>
<tr>
<td align="center" valign="top"><strong>4</strong></td>
<td valign="top"><strong>adab 613</strong>&nbsp; 0.7752<br><br>'Ikrima heard 'A'isha, may Allah be pleased with her, say that she saw the Prophet, may Allah bless him and grant him peace, raise his hands in supplication, saying, 'O Allah, I am only a man, so do not punish me. If I harm or revile a Muslim man, do not punish me for it!'"<br><br><span dir="rtl" lang="ar"><big>‏:‏ اللَّهُمَّ إِنَّمَا أَنَا بَشَرٌ فَلاَ تُعَاقِبْنِي، أَيُّمَا رَجُلٌ مِنَ الْمُؤْمِنِينَ آذَيْتُهُ أَوْ شَتَمْتُهُ فَلا تُعَاقِبْنِي فِيهِ‏.‏</big></span></td>
<td valign="top"><strong>muslim 5724</strong>&nbsp; 0.6049</td>
</tr>
<tr>
<td align="center" valign="top"><strong>5</strong></td>
<td valign="top"><strong>abudawud 2285</strong>&nbsp; 0.7752<br><br>Urwah said: Aisha (Allah be pleased with her) severely objected to the tradition of Fatimah daughter of Qays. She said: Fatimah lived in a desolate house and she feared for her loneliness there. Hence the Messenger of Allah (saws) accorded permission to her (to leave the place).<br><br><span dir="rtl" lang="ar"><big>وا يَا نَبِيَّ اللَّهِ إِنَّ أَبَا حَفْصِ بْنَ الْمُغِيرَةِ طَلَّقَ امْرَأَتَهُ ثَلاَثًا وَإِنَّهُ تَرَكَ لَهَا نَفَقَةً يَسِيرَةً فَقَالَ ‏"‏ لاَ نَفَقَةَ لَهَا ‏"‏ ‏.‏ وَسَاقَ الْحَدِيثَ وَحَدِيثُ مَالِكٍ أَتَمُّ ‏.‏</big></span></td>
<td valign="top"><strong>muslim 4438</strong>&nbsp; 0.6049</td>
</tr>
<tr>
<td align="center" valign="top"><strong>6</strong></td>
<td valign="top"><strong>bukhari 467</strong>&nbsp; 0.7750<br><br>Narrated Masruq: We went to `Aisha while Hassan bin Thabit was with her reciting poetry to her from some of his poetic verses, saying "A chaste wise lady about whom nobody can have suspicion. She gets up with an empty stomach because she never eats the flesh of indiscreet (ladies)." `Aisha said to him, "But you are not like that." I said to her, "Why do you grant him admittance, though Allah said:-- "and as for him among them, who had the greater share therein, his will be a severe torment." (24.11) On that, `Aisha said, "And what punishment is more than blinding?" She, added, "Hassan used to <br><br><span dir="rtl" lang="ar"><big>إِنَّهُ لَيْسَ مِنَ النَّاسِ أَحَدٌ أَمَنَّ عَلَىَّ فِي نَفْسِهِ وَمَالِهِ مِنْ أَبِي بَكْرِ بْنِ أَبِي قُحَافَةَ، وَلَوْ كُنْتُ مُتَّخِذًا مِنَ النَّاسِ خَلِيلاً لاَتَّخَذْتُ أَبَا بَكْرٍ خَلِيلاً، وَلَكِنْ خُلَّةُ الإِسْلاَمِ أَفْضَلُ، سُدُّوا عَنِّي كُلَّ خَوْخَةٍ فِي هَذَا الْمَسْجِدِ غَيْرَ خَوْخَةِ أَبِي بَكْرٍ ‏"</big></span></td>
<td valign="top"><strong>bukhari 413</strong>&nbsp; 0.6049<br><br><span dir="rtl" lang="ar"><big>إِنَّ الْمُؤْمِنَ إِذَا كَانَ فِي الصَّلاَةِ فَإِنَّمَا يُنَاجِي رَبَّهُ، فَلاَ يَبْزُقَنَّ بَيْنَ يَدَيْهِ وَلاَ عَنْ يَمِينِهِ، وَلَكِنْ عَنْ يَسَارِهِ أَوْ تَحْتَ قَدَمِهِ ‏"</big></span></td>
</tr>
<tr>
<td align="center" valign="top"><strong>7</strong></td>
<td valign="top"><strong>bukhari 378</strong>&nbsp; 0.7743 <small>· dup:20400</small><br><br>Narrated `Abdullah bin `Umar: Aisha, (mother of the faithful believers) wanted to buy a slave girl and manumit her, but her masters said that they would sell her only on the condition that her Wala' would be for them. `Aisha told Allah's Apostle of that. He said, "What they stipulate should not hinder you from buying her, as the Wala' is for the manumitted."<br><br><span dir="rtl" lang="ar"><big>إِنَّمَا جُعِلَ الإِمَامُ لِيُؤْتَمَّ بِهِ، فَإِذَا كَبَّرَ فَكَبِّرُوا، وَإِذَا رَكَعَ فَارْكَعُوا، وَإِذَا سَجَدَ فَاسْجُدُوا، وَإِنْ صَلَّى قَائِمًا فَصَلُّوا قِيَامًا ‏"‏‏.‏ وَنَزَلَ لِتِسْعٍ وَعِشْرِينَ فَقَالُوا يَا رَسُولَ اللَّهِ إِنَّكَ آلَيْتَ شَهْرًا فَقَالَ ‏"‏ إِنَّ الشَّهْرَ تِسْعٌ وَعِشْرُونَ ‏"</big></span></td>
<td valign="top"><strong>bukhari 461</strong>&nbsp; 0.6049<br><br><span dir="rtl" lang="ar"><big>إِنَّ عِفْرِيتًا مِنَ الْجِنِّ تَفَلَّتَ عَلَىَّ الْبَارِحَةَ ـ أَوْ كَلِمَةً نَحْوَهَا ـ لِيَقْطَعَ عَلَىَّ الصَّلاَةَ، فَأَمْكَنَنِي اللَّهُ مِنْهُ، فَأَرَدْتُ أَنْ أَرْبِطَهُ إِلَى سَارِيَةٍ مِنْ سَوَارِي الْمَسْجِدِ، حَتَّى تُصْبِحُوا وَتَنْظُرُوا إِلَيْهِ كُلُّكُمْ، فَذَكَرْتُ قَوْلَ أَخِي [name role="nabi"]سُلَيْمَانَ[/name] رَبِّ هَبْ لِي مُلْكًا لاَ يَنْبَغِي لأَحَدٍ مِنْ بَعْدِي ‏"‏‏.‏ قَ</big></span></td>
</tr>
<tr>
<td align="center" valign="top"><strong>8</strong></td>
<td valign="top"><strong>muslim 464</strong>&nbsp; 0.7742<br><br>Salim, the freed slave of Shaddad, said: I came to 'A'isha, the wife of the Holy Prophet (may peace be upon him), on the day when Sa'db. Abi Waqqas died. 'Abd al-Rahman b. Abu Bakr also came there and he performed ablution in her presence. She (Hadrat 'A'isha) said: Abd al-Rahman, complete the ablution as I heard the Allah's Messenger (may peace be upon him) say: Woe to the heels because of hell-fire.</td>
<td valign="top"><strong>tirmidhi 1554</strong>&nbsp; 0.6049<br><br><span dir="rtl" lang="ar"><big>اَ حَدَّثَنَا سُلَيْمُ بْنُ أَخْضَرَ، عَنْ عُبَيْدِ اللَّهِ بْنِ عُمَرَ، عَنْ نَافِعٍ، عَنِ ابْنِ عُمَرَ، أَنَّ رَسُولَ اللَّهِ صلى الله عليه وسلم قَسَمَ فِي النَّفَلِ لِلْفَرَسِ بِسَهْمَيْنِ وَلِلرَّجُلِ بِسَهْمٍ ‏.‏</big></span></td>
</tr>
<tr>
<td align="center" valign="top"><strong>9</strong></td>
<td valign="top"><strong>bukhari 262</strong>&nbsp; 0.7712<br><br>Narrated `Urwa: Aisha during her menses used to comb and oil the hair of the Prophet while he used to be in I`tikaf in the mosque. He would stretch out his head towards her while she was in her chamber.<br><br><span dir="rtl" lang="ar"><big>إِذَا اغْتَسَلَ مِنَ الْجَنَابَةِ غَسَلَ يَدَهُ‏.‏</big></span></td>
<td valign="top"><strong>tirmidhi 1561</strong>&nbsp; 0.6049<br><br><span dir="rtl" lang="ar"><big>الْبُخَارِيُّ لاَ يَصِّحُ حَدِيثُ سُلَيْمَانَ بْنِ مُوسَى إِنَّمَا رَوَاهُ دَاوُدُ بْنُ عَمْرٍو عَنْ أَبِي سَلاَّمٍ عَنِ النَّبِيِّ صلى الله عليه وسلم مُرْسَلاً وَسُلَيْمَانُ بْنُ مُوسَى مُنْكَرُ الْحَدِيثِ أَنَا لاَ أَرْوِي عَنْهُ شَيْئًا رَوَى أَحَادِيثَ مُنْكَرَةً عَامَّتُهَا مِنْهَا حَدِيثُ نَافِعٍ عَنِ ابْنِ عُمَرَ أَنَّ النَّبِيَّ صلى الله عليه وسلم كُفِّنَ فِي ثَلاَثَةِ أَثْوَابٍ ‏.‏ وَحَدِ</big></span></td>
</tr>
<tr>
<td align="center" valign="top"><strong>10</strong></td>
<td valign="top"><strong>bukhari 245</strong>&nbsp; 0.7707<br><br>Narrated 'Urwa: Aisha disapproved of what Fatima used to say.'<br><br><span dir="rtl" lang="ar"><big>إِذَا قَامَ مِنَ اللَّيْلِ يَشُوصُ فَاهُ بِالسِّوَاكِ‏.‏</big></span></td>
<td valign="top"><strong>tirmidhi 1705</strong>&nbsp; 0.6049<br><br><span dir="rtl" lang="ar"><big>‏"‏ أَلاَ كُلُّكُمْ رَاعٍ وَكُلُّكُمْ مَسْئُولٌ عَنْ رَعِيَّتِهِ فَالأَمِيرُ الَّذِي عَلَى النَّاسِ رَاعٍ وَمَسْئُولٌ عَنْ رَعِيَّتِهِ وَالرَّجُلُ رَاعٍ عَلَى أَهْلِ بَيْتِهِ وَهُوَ مَسْئُولٌ عَنْهُمْ وَالْمَرْأَةُ رَاعِيَةٌ عَلَى بَيْتِ بَعْلِهَا وَهِيَ مَسْئُولَةٌ عَنْهُ وَالْعَبْدُ رَاعٍ عَلَى مَالِ سَيِّدِهِ وَهُوَ مَسْئُولٌ عَنْهُ أَلاَ فَكُلُّكُمْ رَاعٍ وَكُلُّكُمْ مَسْئُولٌ عَنْ رَعِيَّتِهِ</big></span></td>
</tr>
</tbody></table>

## Arabic / Multilingual OpenAI

<table width="100%"><thead><tr>
<th width="4%">#</th>
<th width="19%">Arabic OpenAI (small)</th>
<th width="19%">Arabic OpenAI (large)</th>
<th width="19%">E5 Multilingual</th>
<th width="19%">BGE-M3</th>
<th width="19%">Qwen3-Embed</th>
</tr></thead><tbody>
<tr>
<td align="center" valign="top"><strong>1</strong></td>
<td valign="top"><strong>bukhari 4752</strong>&nbsp; 0.6891<br><br><em><small>⛓ Narrated Ibn Abi Mulaika:</small></em><br><br>I heard `Aisha reciting: "When you invented a lie (and carry it) on your tongues." (24.15)<br><br><span dir="rtl" lang="ar"><big>عَائِشَةَ، تَقْرَأُ ‏ {‏إِذْ تَلِقُونَهُ بِأَلْسِنَتِكُمْ‏} ‏</big></span></td>
<td valign="top"><strong>muslim 1321 m</strong>&nbsp; 0.7200<br><br><em><small>⛓ Masruq reported:</small></em><br><br>I heard 'A'isha (Allah be pleased with her) clapping her hands behind the curtain and saying: I used to weave garlands for the sacrificial animals of Allah's Messenger (may peace be upon him) with my own hands, and then he (the Holy Prophet) sent them (to Mecca), and he did not avoid doing anything which a Muhritn avoids until his animal was sacrificed.<br><br><span dir="rtl" lang="ar"><big>عَائِشَةَ، وَهْىَ مِنْ وَرَاءِ الْحِجَابِ تُصَفِّقُ وَتَقُولُ كُنْتُ أَفْتِلُ قَلاَئِدَ هَدْىِ رَسُولِ اللَّهِ صلى الله عليه وسلم بِيَدَىَّ ثُمَّ يَبْعَثُ بِهَا وَمَا يُمْسِكُ عَنْ شَىْءٍ مِمَّا يُمْسِكُ عَنْهُ الْمُحْرِمُ حَتَّى يُنْحَرَ هَدْيُهُ.</big></span></td>
<td valign="top"><strong>bukhari 5158</strong>&nbsp; 0.9211<br><br>Narrated 'Urwa: The Prophet wrote the (marriage contract) with `Aisha while she was six years old and consummated his marriage with her while she was nine years old and she remained with him for nine years (i.e. till his death).<br><br><span dir="rtl" lang="ar"><big>تَزَوَّجَ النَّبِيُّ صلى الله عليه وسلم عَائِشَةَ وَهْىَ ابْنَةُ سِتٍّ وَبَنَى بِهَا وَهْىَ ابْنَةُ تِسْعٍ وَمَكَثَتْ عِنْدَهُ تِسْعًا‏.‏</big></span></td>
<td valign="top"><em>ERROR: HTTP Error 404: NOT FOUND</em></td>
<td valign="top"><em>ERROR: HTTP Error 500: INTERNAL SERVER ERROR</em></td>
</tr>
<tr>
<td align="center" valign="top"><strong>2</strong></td>
<td valign="top"><strong>bukhari 2628</strong>&nbsp; 0.6753<br><br><em><small>⛓ Narrated Aiman:</small></em><br><br>I went to `Aisha and she was wearing a coarse dress costing five Dirhams. `Aisha said, "Look up and see my slave-girl who refuses to wear it in the house though during the lifetime of Allah's Apostle I had a similar dress which no woman desiring to appear elegant (before her husband) failed to borrow from me."<br><br><span dir="rtl" lang="ar"><big>دَخَلْتُ عَلَى عَائِشَةَ ـ رضى الله عنها ـ وَعَلَيْهَا دِرْعُ قِطْرٍ ثَمَنُ خَمْسَةِ دَرَاهِمَ، فَقَالَتِ ارْفَعْ بَصَرَكَ إِلَى جَارِيَتِي، انْظُرْ إِلَيْهَا فَإِنَّهَا تُزْهَى أَنْ تَلْبَسَهُ فِي الْبَيْتِ، وَقَدْ كَانَ لِي مِنْهُنَّ دِرْعٌ عَلَى عَهْدِ رَسُولِ اللَّهِ صلى الله عليه وسلم، فَمَا كَانَتِ امْرَأَةٌ تُقَيَّنُ [place]بِالْمَدِينَةِ [/place]إِلاَّ أَرْسَلَتْ إِلَىَّ تَسْتَعِيرُهُ‏.‏</big></span></td>
<td valign="top"><strong>muslim 1211 o</strong>&nbsp; 0.7189<br><br>AI-Qasim b. Muhammad reported that A'isha had come for Hajj.<br><br><span dir="rtl" lang="ar"><big>جَاءَتْ عَائِشَةُ حَاجَّةً ‏.‏</big></span></td>
<td valign="top"><strong>bukhari 5818</strong>&nbsp; 0.9190<br><br>Narrated Abu Burda: Aisha brought out to us a Kisa and an Izar and said, "The Prophet died while wearing these two." (Kisa, a square black piece of woolen cloth. Izar, a sheet cloth garment covering the lower half of the body).<br><br><span dir="rtl" lang="ar"><big>قُبِضَ رُوحُ النَّبِيِّ صلى الله عليه وسلم فِي هَذَيْنِ‏.‏</big></span></td>
<td valign="top"><em>ERROR: HTTP Error 404: NOT FOUND</em></td>
<td valign="top"><em>ERROR: HTTP Error 500: INTERNAL SERVER ERROR</em></td>
</tr>
<tr>
<td align="center" valign="top"><strong>3</strong></td>
<td valign="top"><strong>bukhari 1641, 1642</strong>&nbsp; 0.6703<br><br><em><small>⛓ Narrated Muhammad bin `Abdur-Rahman bin Nawfal Al-Qurashi:</small></em><br><br>I asked `Urwa bin Az-Zubair (regarding the Hajj of the Prophet ). `Urwa replied, "Aisha narrated, 'When the Prophet reached Mecca, the first thing he started with was the ablution, then he performed Tawaf of the Ka`ba and his intention was not `Umra alone (but Hajj and `Umra together).' " Later Abu Bakr I performed the Hajj and the first thing he started with was Tawaf of the Ka`ba and it was not `Umra alone (but Hajj and `Umra together). And then `Umar did the same. Then `Uthman performed the Hajj and the first thing he started with was Tawaf of the Ka`ba and it was not `Umra alone. And then <br><br><span dir="rtl" lang="ar"><big>حَجَّ النَّبِيُّ صلى الله عليه وسلم فَأَخْبَرَتْنِي عَائِشَةُ ـ رضى الله عنها ـ أَنَّهُ أَوَّلُ شَىْءٍ بَدَأَ بِهِ حِينَ قَدِمَ أَنَّهُ تَوَضَّأَ ثُمَّ طَافَ [place]بِالْبَيْتِ[/place] ثُمَّ لَمْ تَكُنْ عُمْرَةً</big></span></td>
<td valign="top"><strong>ibnkhuzayma </strong>&nbsp; 0.7186<br><br><span dir="rtl" lang="ar"><big>أَعْمَرَ عَائِشَةَ مِنَ التَّنْعِيمِ فِي ذِي الْحِجَّةِ "</big></span></td>
<td valign="top"><strong>bukhari 6249</strong>&nbsp; 0.9190<br><br>Narrated `Aisha: Allah's Apostle said, "O `Aisha! This is Gabriel sending his greetings to you." I said, "Peace, and Allah's Mercy be on him (Gabriel). You see what we do not see." (She was addressing Allah's Apostle).<br><br><span dir="rtl" lang="ar"><big>هَذَا [name role="angel"]جِبْرِيلُ [/name]يَقْرَأُ عَلَيْكِ السَّلاَمَ ‏"‏‏.‏ قَالَتْ قُلْتُ وَعَلَيْهِ السَّلاَمُ وَرَحْمَةُ اللَّهِ، تَرَى مَا لاَ نَرَى</big></span></td>
<td valign="top"><em>ERROR: HTTP Error 404: NOT FOUND</em></td>
<td valign="top"><em>ERROR: HTTP Error 500: INTERNAL SERVER ERROR</em></td>
</tr>
<tr>
<td align="center" valign="top"><strong>4</strong></td>
<td valign="top"><strong>muslim 738 e</strong>&nbsp; 0.6687<br><br>It is reported on the authority of 'A'isha that the prayer of Allah's Messenger (may peace be upon him) in the night consisted of ten rak'ahs. He observed a Witr and two rak'ahs (of Sunan) of the dawn prayer, and thus the total comes to thirteen rak'ahs.<br><br><span dir="rtl" lang="ar"><big>عَائِشَةَ، تَقُولُ كَانَتْ صَلاَةُ رَسُولِ اللَّهِ صلى الله عليه وسلم مِنَ اللَّيْلِ عَشَرَ رَكَعَاتٍ وَيُوتِرُ بِسَجْدَةٍ وَيَرْكَعُ رَكْعَتَىِ الْفَجْرِ فَتِلْكَ ثَلاَثَ عَشْرَةَ رَكْعَةً ‏.‏</big></span></td>
<td valign="top"><strong>ibnabishayba </strong>&nbsp; 0.7182<br><br><span dir="rtl" lang="ar"><big>ابْنَةً لِعُمَرَ كَانَ يُقَالُ لَهَا : عَاصِيَةُ , " فَسَمَّاهَا رَسُولُ اللَّهِ صَلَّى اللَّهُ عَلَيْهِ وَسَلَّمَ جَمِيلَةَ "</big></span></td>
<td valign="top"><strong>bukhari 6068</strong>&nbsp; 0.9171<br><br>Narrated Al-Laith: `Aisha said "The Prophet entered upon me one day and said, 'O `Aisha! I do not think that so-and-so and so-and-so know anything of our religion which we follow."'<br><br><span dir="rtl" lang="ar"><big>‏"‏ يَا عَائِشَةُ مَا أَظُنُّ فُلاَنًا وَفُلاَنًا يَعْرِفَانِ دِينَنَا الَّذِي نَحْنُ عَلَيْهِ ‏"[/postmatn]‏‏.‏</big></span></td>
<td valign="top"><em>ERROR: HTTP Error 404: NOT FOUND</em></td>
<td valign="top"><em>ERROR: HTTP Error 500: INTERNAL SERVER ERROR</em></td>
</tr>
<tr>
<td align="center" valign="top"><strong>5</strong></td>
<td valign="top"><strong>abudawud 1341</strong>&nbsp; 0.6675<br><br><em><small>⛓ Abu Salamah b. 'Abd al-Rahman asked 'Aishah, the wife of the Prophet (saws): How did the Messenger of Allah (saws) pray during Ramadhan ? She said:</small></em><br><br>The Messenger of Allah (saws) did not pray more than eleven rak'ahs during Ramadhan and other than Ramadhan. He would pray four rak'ahs. Do not ask about their elegance and length. He then would pray for rak'ahs. Do not ask about their alegance and length. Then he would pray three rak'ahs. 'Aishah said: I asked: Messenger of Allah, do you sleep before observing witr ? He replied: 'Aishah, my eyes sleep, but my heart does not sleep.<br><br><span dir="rtl" lang="ar"><big>‏:‏ ‏"‏ يَا عَائِشَةُ إِنَّ عَيْنَىَّ تَنَامَانِ وَلاَ يَنَامُ قَلْبِي ‏"‏ ‏.‏</big></span></td>
<td valign="top"><strong>hakim </strong>&nbsp; 0.7168<br><br><span dir="rtl" lang="ar"><big>" عَائِشَةُ بِنْتُ أَبِي بَكْرٍ الصِّدِّيقِ رَضِيَ اللَّهُ ، عَنْهَا أُمُّهَا أُمُّ رُومَانَ بِنْتُ عَامِرِ بْنِ عُوَيْمِرِ بْنِ عَبْدِ شَمْسِ بْنِ عَتَّابِ بْنِ أُذَيْنَةَ بْنِ سُبَيْعِ بْنِ دُهْمَانَ بْنِ الْحَارِثِ بْنِ غَنْمِ بْنِ مَالِكِ بْنِ كِنَانَةَ ، تَزَوَّجَهَا رَسُولُ اللَّهِ صَلَّى اللَّهُ عَلَيْهِ وَآَلِهِ وَسَلَّمَ فِي شَوَّالٍ سَنَةَ عَشْرٍ مِنَ النُّبُوَّةِ ، قَبْلَ الْهِجْرَةِ بِ</big></span></td>
<td valign="top"><strong>shamail 174</strong>&nbsp; 0.9166<br><br>Anas ibn Malik said: “Allah’s Messenger said (Allah bless him and give him peace):‘The superiority of 'A'isha over all other women is like the superiority of tharid [a dish of sopped bread, meat and broth] over all other food'.”<br><br><span dir="rtl" lang="ar"><big>صلى الله عليه وسلم‏:‏ فَضْلُ عَائِشَةَ عَلَى النِّسَاءِ كَفَضْلِ الثَّرِيدِ عَلَى سَائِرِ الطَّعَامِ‏.‏</big></span></td>
<td valign="top"><em>ERROR: HTTP Error 404: NOT FOUND</em></td>
<td valign="top"><em>ERROR: HTTP Error 500: INTERNAL SERVER ERROR</em></td>
</tr>
<tr>
<td align="center" valign="top"><strong>6</strong></td>
<td valign="top"><strong>bukhari 4872</strong>&nbsp; 0.6673<br><br><em><small>⛓ Narrated `Abdullah bin Masud:</small></em><br><br>The Prophet used to recite: "Fahal-min-Maddakir (then is there any that will receive admonition?")<br><br><span dir="rtl" lang="ar"><big>‏ {‏فَهَلْ مِنْ مُدَّكِرٍ‏} ‏ الآيَةَ‏.‏</big></span></td>
<td valign="top"><strong>muslim 1479 d</strong>&nbsp; 0.7165<br><br><em><small>⛓ Ibn Abbas (Allah be pleased with them) is reported to have said:</small></em><br><br>I intended to ask Umar about those two ladies who had pressed for (worldly riches) during the lifetime of the Holy Prophet (may peace be upon him), and I kept waiting for one year, but found no suitable opportunity with him until I happened to accompany him to Mecca. And as he reached Marr al Zahran he went away to answer the call of nature, and he said (to me): Bring me a jug of water, and I took that to him. After having answered the call of nature, as he came back, I began to pour water (over his hands and feet), and I remembered (this event of separation of Allah's Apostle [may peace be up<br><br><span dir="rtl" lang="ar"><big>عَائِشَةُ وَحَفْصَةُ ‏.‏</big></span></td>
<td valign="top"><strong>bukhari 4752</strong>&nbsp; 0.9162<br><br>Narrated Ibn Abi Mulaika: I heard `Aisha reciting: "When you invented a lie (and carry it) on your tongues." (24.15)<br><br><span dir="rtl" lang="ar"><big>عَائِشَةَ، تَقْرَأُ ‏ {‏إِذْ تَلِقُونَهُ بِأَلْسِنَتِكُمْ‏} ‏</big></span></td>
<td valign="top"><em>ERROR: HTTP Error 404: NOT FOUND</em></td>
<td valign="top"><em>ERROR: HTTP Error 500: INTERNAL SERVER ERROR</em></td>
</tr>
<tr>
<td align="center" valign="top"><strong>7</strong></td>
<td valign="top"><strong>tirmidhi 588</strong>&nbsp; 0.6656<br><br><em><small>⛓ Sa'eed bin Abi Hind narrated from some of the companions of Ikrimah:</small></em><br><br>"The Prophet would glance during Salat" and he mentioned a similar narration.<br><br><span dir="rtl" lang="ar"><big>وَفِي الْبَابِ عَنْ أَنَسٍ وَعَائِشَةَ ‏.‏</big></span></td>
<td valign="top"><strong>ibnabishayba </strong>&nbsp; 0.7164<br><br><span dir="rtl" lang="ar"><big>قَبَّلَ رَأْسَ عَائِشَةَ "</big></span></td>
<td valign="top"><strong>mishkat 3129</strong>&nbsp; 0.9160<br><br>‘A’isha said that the Prophet married her when she was seven, she was brought to live with him when she was nine bringing her toys with her, and he died when she was eighteen. Muslim transmitted it.<br><br><span dir="rtl" lang="ar"><big>وَعَنْ عَائِشَةَ أَنَّ النَّبِيَّ صَلَّى اللَّهُ عَلَيْهِ وَسَلَّمَ تَزَوَّجَهَا وَهِيَ بِنْتُ سَبْعِ سِنِينَ وَزُفَّتْ إِلَيْهِ وَهِيَ بِنْتُ تِسْعِ سِنِينَ وَلُعَبُهَا مَعَهَا وَمَاتَ عَنْهَا وَهِيَ بِنْتُ ثَمَانِيَ عَشْرَةَ. رَوَاهُ مُسلم</big></span></td>
<td valign="top"><em>ERROR: HTTP Error 404: NOT FOUND</em></td>
<td valign="top"><em>ERROR: HTTP Error 500: INTERNAL SERVER ERROR</em></td>
</tr>
<tr>
<td align="center" valign="top"><strong>8</strong></td>
<td valign="top"><strong>tirmidhi 1839</strong>&nbsp; 0.6651<br><br><em><small>⛓ Narrated Jabir:</small></em><br><br>That the Prophet (saws) said: "What an excellent condiment vinegar is."<br><br><span dir="rtl" lang="ar"><big>‏"‏ نِعْمَ الإِدَامُ الْخَلُّ ‏"‏ ‏.‏ قَالَ وَفِي الْبَابِ عَنْ عَائِشَةَ وَأُمِّ هَانِئٍ ‏.‏</big></span></td>
<td valign="top"><strong>hakim </strong>&nbsp; 0.7147<br><br><span dir="rtl" lang="ar"><big>" هَلْ كَانَتْ عَائِشَةُ تُحْسِنُ الْفَرَائِضَ ؟ قَالَ : إِي وَالَّذِي نَفْسِي بِيَدِهِ ، لَقَدْ رَأَيْتُ مَشْيَخَةَ أَصْحَابِ مُحَمَّدٍ صَلَّى اللَّهُ عَلَيْهِ وَآَلِهِ وَسَلَّمَ ، يَسْأَلُونَهَا عَنِ الْفَرَائِضِ "</big></span></td>
<td valign="top"><strong>muslim 2815</strong>&nbsp; 0.9157<br><br>A'isha the wife of Allah's Apostle (may peace be upon him), reported that one day Allah's Messenger (may peace be upon him) came out of her (apartment) during the night and she felt jealous. Then he came and he saw me (in what agitated state of mind) I was. He said: A'isha, what has happened to you? Do you feel jealous? Thereupon she said: How can it be (that a woman like me) should not feel jealous in regard to a husband like you. Thereupon Allah's Messenger (may peace be upon him) said: It was your devil who had come to you, and she said: Allah's Messenger, is there along with me a devil? He<br><br><span dir="rtl" lang="ar"><big>‏"‏ نَعَمْ وَلَكِنْ رَبِّي أَعَانَنِي عَلَيْهِ حَتَّى أَسْلَمَ ‏"‏ ‏.‏</big></span></td>
<td valign="top"><em>ERROR: HTTP Error 404: NOT FOUND</em></td>
<td valign="top"><em>ERROR: HTTP Error 500: INTERNAL SERVER ERROR</em></td>
</tr>
<tr>
<td align="center" valign="top"><strong>9</strong></td>
<td valign="top"><strong>muslim 1479 d</strong>&nbsp; 0.6650<br><br><em><small>⛓ Ibn Abbas (Allah be pleased with them) is reported to have said:</small></em><br><br>I intended to ask Umar about those two ladies who had pressed for (worldly riches) during the lifetime of the Holy Prophet (may peace be upon him), and I kept waiting for one year, but found no suitable opportunity with him until I happened to accompany him to Mecca. And as he reached Marr al Zahran he went away to answer the call of nature, and he said (to me): Bring me a jug of water, and I took that to him. After having answered the call of nature, as he came back, I began to pour water (over his hands and feet), and I remembered (this event of separation of Allah's Apostle [may peace be up<br><br><span dir="rtl" lang="ar"><big>عَائِشَةُ وَحَفْصَةُ ‏.‏</big></span></td>
<td valign="top"><strong>ibnkhuzayma </strong>&nbsp; 0.7131<br><br><span dir="rtl" lang="ar"><big>أَعْمَرَ عَائِشَةَ مِنَ التَّنْعِيمِ لَيْلَةَ الْحَصْبَةِ "</big></span></td>
<td valign="top"><strong>bukhari 4751</strong>&nbsp; 0.9151<br><br>Narrated Um Ruman: Aisha's mother, When `Aisha was accused, she fell down Unconscious.<br><br><span dir="rtl" lang="ar"><big>لَمَّا رُمِيَتْ عَائِشَةُ خَرَّتْ مَغْشِيًّا عَلَيْهَا‏.‏</big></span></td>
<td valign="top"><em>ERROR: HTTP Error 404: NOT FOUND</em></td>
<td valign="top"><em>ERROR: HTTP Error 500: INTERNAL SERVER ERROR</em></td>
</tr>
<tr>
<td align="center" valign="top"><strong>10</strong></td>
<td valign="top"><strong>muslim 1321 d</strong>&nbsp; 0.6642<br><br><em><small>⛓ Abd al-Rahman b. al-Qasim reported on the authority of his father that he heard 'A'isha (Allah be pleased with her) saying:</small></em><br><br>I used to weave garlands for the sacrificial animals of Allah's Messenger (may peace be upon him) with these hands of mine, but he (Allah's Apostle) neither avoided anything nor gave up anything (which a Muhrim should avoid or give up).<br><br><span dir="rtl" lang="ar"><big>عَائِشَةَ، تَقُولُ كُنْتُ أَفْتِلُ قَلاَئِدَ هَدْىِ رَسُولِ اللَّهِ صلى الله عليه وسلم بِيَدَىَّ هَاتَيْنِ ثُمَّ لاَ يَعْتَزِلُ شَيْئًا وَلاَ يَتْرُكُهُ.</big></span></td>
<td valign="top"><strong>ahmad 339</strong>&nbsp; 0.7110<br><br><em><small>⛓ It was narrated that Ibn `Abbas said:</small></em><br><br>I wanted to ask `Umar something but I did not find a chance, so I waited for two years. Then when we were in Marraz-Zahran, he went to relieve himself, then he came after relieving himself and I poured water for him, I said: O Ameer al-Mu`mineen, who are the two women who helped one another against the Messenger of Allah (ﷺ)`? He said: `A`ishah and Hafsah. ` As mentioned in the Qur`an: `If you two (wives of the Prophet (ﷺ)) turn in repentance to Allâh. (it will be better for you), your hearts are indeed so inclined to oppose what the Prophet (ﷺ) likes); but if you help one another against him <br><br><span dir="rtl" lang="ar"><big>عَائِشَةُ وَحَفْصَةُ رَضِيَ اللَّهُ عَنْهُمَا‏.‏</big></span></td>
<td valign="top"><strong>shamail 118</strong>&nbsp; 0.9151<br><br>Abu Burda reported that his father said: “'A'isha (may Allah be well pleased with her) brought out to us a tangled garment and a coarse loincloth, then she said: ‘The spirit of Allah’s Messenger (Allah bless him and give him peace) was taken in these two'.”<br><br><span dir="rtl" lang="ar"><big>تْ‏:‏ قُبِضَ رُوحُ رَسُولِ اللهِ صلى الله عليه وسلم، فِي هَذَيْنِ‏.‏</big></span></td>
<td valign="top"><em>ERROR: HTTP Error 404: NOT FOUND</em></td>
<td valign="top"><em>ERROR: HTTP Error 500: INTERNAL SERVER ERROR</em></td>
</tr>
</tbody></table>

---

# Query: "comparing yourself to others"

**Latency:** **BM25 Lexical (full text)** 55ms · **Mixedbread (noisy — full hadithText)** 128ms · **Mixedbread (clean matn)** 130ms · **English OpenAI small (clean matn)** 237ms · **English OpenAI large (clean matn)** 903ms · **Arabic OpenAI (small)** 195ms · **Arabic OpenAI (large)** 291ms · **E5 Multilingual** 177ms  
**Arabic OpenAI (small) clusters:** [70, 64]  
**Arabic OpenAI (large) clusters:** [108, 134]  

## BM25 · Mixedbread

<table width="100%"><thead><tr>
<th width="4%">#</th>
<th width="32%">BM25 Lexical (full text)</th>
<th width="32%">Mixedbread (noisy — full hadithText)</th>
<th width="32%">Mixedbread (clean matn)</th>
</tr></thead><tbody>
<tr>
<td align="center" valign="top"><strong>1</strong></td>
<td valign="top"><strong>bukhari 3334</strong>&nbsp; 16.2567<br><br>Narrated Anas: The Prophet said, "Allah will say to that person of the (Hell) Fire who will receive the least punishment, 'If you had everything on the earth, would you give it as a ransom to free yourself (i.e. save yourself from this Fire)?' He will say, 'Yes.' Then Allah will say, 'While you were in the backbone of Adam, I asked you much less than this, i.e. not to worship others besides Me, but you insisted on worshipping others besides me.' "<br><br><span dir="rtl" lang="ar"><big>لأَهْوَنِ أَهْلِ النَّارِ عَذَابًا لَوْ أَنَّ لَكَ مَا فِي الأَرْضِ مِنْ شَىْءٍ كُنْتَ تَفْتَدِي بِهِ قَالَ نَعَمْ‏.‏ قَالَ فَقَدْ سَأَلْتُكَ مَا هُوَ أَهْوَنُ مِنْ هَذَا وَأَنْتَ فِي صُلْبِ [name role="nabi"]آدَمَ [/name]أَنْ لاَ تُشْرِكَ بِي‏.‏ فَأَبَيْتَ إِلاَّ الشِّرْكَ ‏"</big></span></td>
<td valign="top"><strong>forty 18</strong>&nbsp; 0.8140<br><br>The felicitous person takes lessons from (the actions of) others.<br><br><span dir="rtl" lang="ar"><big>عَنْ أَبِي ذَرٍّ جُنْدَبِ بْنِ جُنَادَةَ، وَأَبِي عَبْدِ الرَّحْمَنِ مُعَاذِ بْنِ جَبَلٍ رَضِيَ اللَّهُ عَنْهُمَا، عَنْ رَسُولِ اللَّهِ صلى الله عليه و سلم قَالَ: "اتَّقِ اللَّهَ حَيْثُمَا كُنْت، وَأَتْبِعْ السَّيِّئَةَ الْحَسَنَةَ تَمْحُهَا، وَخَالِقْ النَّاسَ بِخُلُقٍ حَسَنٍ" . رَوَاهُ التِّرْمِذِيُّ [رقم:1987] وَقَالَ: حَدِيثٌ حَسَنٌ، وَفِي بَعْضِ النُّسَخِ: حَسَنٌ صَحِيحٌ.</big></span></td>
<td valign="top"><strong>muslim 2963 a</strong>&nbsp; 0.8621<br><br><em><small>⛓ Abu Huraira reported that Allah's Messenger (may peace be upon him) said:</small></em><br><br>When one of you looks at one who stands at a higher level than you in regard to wealth and physical structure he should also see one who stands at a lower level than you in regard to these things (in which he stands) at a higher level (as compared to him).<br><br><span dir="rtl" lang="ar"><big>‏"‏ إِذَا نَظَرَ أَحَدُكُمْ إِلَى مَنْ فُضِّلَ عَلَيْهِ فِي الْمَالِ وَالْخَلْقِ فَلْيَنْظُرْ إِلَى مَنْ هُوَ أَسْفَلَ مِنْهُ مِمَّنْ فُضِّلَ عَلَيْهِ ‏"‏ ‏.‏</big></span></td>
</tr>
<tr>
<td align="center" valign="top"><strong>2</strong></td>
<td valign="top"><strong>muslim 2431</strong>&nbsp; 16.1906 <small>· dup:259660</small><br><br>Abu Musa reported Allah's Messenger (may peace be upon him) as saying: There are many persons amongst men who are quite perfect but there are none perfect amongst women except Mary, daughter of 'Imran, Asiya wife of Pharaoh, and the excellence of 'A'isha as compared to women is that of Tharid over all other foods.<br><br><span dir="rtl" lang="ar"><big>صلى الله عليه وسلم ‏"‏ كَمَلَ مِنَ الرِّجَالِ كَثِيرٌ وَلَمْ يَكْمُلْ مِنَ النِّسَاءِ غَيْرُ مَرْيَمَ بِنْتِ عِمْرَانَ وَآسِيَةَ امْرَأَةِ فِرْعَوْنَ وَإِنَّ فَضْلَ عَائِشَةَ عَلَى النِّسَاءِ كَفَضْلِ الثَّرِيدِ عَلَى سَائِرِ الطَّعَامِ ‏"‏ ‏.‏</big></span></td>
<td valign="top"><strong>bukhari 6490</strong>&nbsp; 0.8063<br><br><em><small>⛓ Narrated Abu Huraira:</small></em><br><br>Allah's Apostle said, "If anyone of you looked at a person who was made superior to him in property and (in good) appearance, then he should also look at the one who is inferior to him.<br><br><span dir="rtl" lang="ar"><big>إِذَا نَظَرَ أَحَدُكُمْ إِلَى مَنْ فُضِّلَ عَلَيْهِ فِي الْمَالِ وَالْخَلْقِ، فَلْيَنْظُرْ إِلَى مَنْ هُوَ أَسْفَلَ مِنْهُ ‏"</big></span></td>
<td valign="top"><strong>bukhari 6490</strong>&nbsp; 0.8141<br><br><em><small>⛓ Narrated Abu Huraira:</small></em><br><br>Allah's Apostle said, "If anyone of you looked at a person who was made superior to him in property and (in good) appearance, then he should also look at the one who is inferior to him.<br><br><span dir="rtl" lang="ar"><big>إِذَا نَظَرَ أَحَدُكُمْ إِلَى مَنْ فُضِّلَ عَلَيْهِ فِي الْمَالِ وَالْخَلْقِ، فَلْيَنْظُرْ إِلَى مَنْ هُوَ أَسْفَلَ مِنْهُ ‏"</big></span></td>
</tr>
<tr>
<td align="center" valign="top"><strong>3</strong></td>
<td valign="top"><strong>bukhari 4816</strong>&nbsp; 14.8967<br><br>Narrated Ibn Mas`ud: (regarding) the Verse: 'And you have not been screening against yourself lest your ears, and your eyes and your skins should testify against you..' (41.22) While two persons from Quraish and their brotherin- law from Thaqif (or two persons from Thaqif and their brother-in-law from Quraish) were in a house, they said to each other, "Do you think that Allah hears our talks?" Some said, "He hears a portion thereof" Others said, "If He can hear a portion of it, He can hear all of it." Then the following Verse was revealed: 'And you have not been screening against yourself lest<br><br><span dir="rtl" lang="ar"><big>أَتُرَوْنَ أَنَّ اللَّهَ يَسْمَعُ حَدِيثَنَا قَالَ بَعْضُهُمْ يَسْمَعُ بَعْضَهُ‏.‏ وَقَالَ بَعْضُهُمْ لَئِنْ كَانَ يَسْمَعُ بَعْضَهُ لَقَدْ يَسْمَعُ كُلَّهُ‏.‏ فَأُنْزِلَتْ ‏ {‏وَمَا كُنْتُمْ تَسْتَتِرُونَ أَنْ يَشْهَدَ عَلَيْكُمْ سَمْعُكُمْ وَلاَ أَبْصَارُكُمْ‏} ‏ الآية</big></span></td>
<td valign="top"><strong>ibnmajah 4336</strong>&nbsp; 0.7919<br><br><em><small>⛓ Sa’eed bin Al-Musayyab said that he met Abu Hurairah and Abu Hurairah said:</small></em><br><br>“I supplicate Allah to bring you and I together in the marketplace of Paradise,” Sa’eed said: “Is there a marketplace there?” He said: “Yes. The Messenger of Allah (saw) told me that when the people of Paradise enter it, they will take their places according to their deeds, and they will be given permission for a length of time equivalent to Friday on earth, when they will visit Allah. His Throne will be shown to them and He will appear to them in one of the gardens of Paradise. Chairs of light and chairs of pearls and chairs of rubies and chairs of chrysolite and chairs of gold and chairs of <br><br><span dir="rtl" lang="ar"><big>‏"‏ نَعَمْ هَلْ تَتَمَارَوْنَ فِي رُؤْيَةِ الشَّمْسِ وَالْقَمَرِ لَيْلَةَ الْبَدْرِ ‏"‏ ‏.‏ قُلْنَا لاَ ‏.‏ قَالَ ‏"‏ كَذَلِكَ لاَ تَتَمَارَوْنَ فِي رُؤْيَةِ رَبِّكُمْ عَزَّ وَجَلَّ وَلاَ يَبْقَى فِي ذَلِكَ الْمَجْلِسِ أَحَدٌ إِلاَّ حَاضَرَهُ اللَّهُ عَزَّ وَجَلَّ مُحَاضَرَةً حَتَّى إِنَّهُ يَقُولُ لِلرَّجُلِ مِنْكُمْ أَلاَ تَذْكُرُ يَا فُلاَنُ يَوْمَ عَمِلْتَ كَذَا وَكَذَا - يُذَكِّرُهُ بَعْضَ غَ</big></span></td>
<td valign="top"><strong>forty 18</strong>&nbsp; 0.8137<br><br>The felicitous person takes lessons from (the actions of) others.<br><br><span dir="rtl" lang="ar"><big>عَنْ أَبِي ذَرٍّ جُنْدَبِ بْنِ جُنَادَةَ، وَأَبِي عَبْدِ الرَّحْمَنِ مُعَاذِ بْنِ جَبَلٍ رَضِيَ اللَّهُ عَنْهُمَا، عَنْ رَسُولِ اللَّهِ صلى الله عليه و سلم قَالَ: "اتَّقِ اللَّهَ حَيْثُمَا كُنْت، وَأَتْبِعْ السَّيِّئَةَ الْحَسَنَةَ تَمْحُهَا، وَخَالِقْ النَّاسَ بِخُلُقٍ حَسَنٍ" . رَوَاهُ التِّرْمِذِيُّ [رقم:1987] وَقَالَ: حَدِيثٌ حَسَنٌ، وَفِي بَعْضِ النُّسَخِ: حَسَنٌ صَحِيحٌ.</big></span></td>
</tr>
<tr>
<td align="center" valign="top"><strong>4</strong></td>
<td valign="top"><strong>muslim 2939 b</strong>&nbsp; 14.8815<br><br>Mughira b. Shu'ba reported that none asked Allah's Apostle (may peace be upon him) about Dajjal more than I asked him. I (one of the narrators other than Mughira b. Shu'ba) said: What did you ask? Mughira replied: I said that the people alleged that he would have a mountain load of bread and mutton and rivers of water. Thereupon he said: He would be more insignificant in the eye of Allah compared with all this.<br><br><span dir="rtl" lang="ar"><big>‏"‏ وَمَا سُؤَالُكَ ‏"‏ ‏.‏ قَالَ قُلْتُ إِنَّهُمْ يَقُولُونَ مَعَهُ جِبَالٌ مِنْ خُبْزٍ وَلَحْمٍ وَنَهَرٌ مِنْ مَاءٍ ‏.‏ قَالَ ‏"‏ هُوَ أَهْوَنُ عَلَى اللَّهِ مِنْ ذَلِكَ ‏"‏ ‏.‏</big></span></td>
<td valign="top"><strong>adab 159</strong>&nbsp; 0.7905<br><br>Abu'd-Darda' used to say to people. "We know you better than the veterinarian knows his animals. We recognise the best of you from the worst of you. The best of you is the one whose good is hoped for and the one whose evil you are safe from. As for the worst of you, that is the person whose good is not hoped for and whose evil you are not safe from and he does not free slaves."<br><br><span dir="rtl" lang="ar"><big>لِلنَّاسِ‏:‏ نَحْنُ أَعْرَفُ بِكُمْ مِنَ الْبَيَاطِرَةِ بِالدَّوَابِّ، قَدْ عَرَفْنَا خِيَارَكُمْ مِنْ شِرَارِكُمْ‏.‏ أَمَّا خِيَارُكُمُ‏:‏ الَّذِي يُرْجَى خَيْرُهُ، وَيُؤْمَنُ شَرُّهُ‏.‏ وَأَمَّا شِرَارُكُمْ‏:‏ فَالَّذِي لاَ يُرْجَى خَيْرُهُ، وَلاَ يُؤْمَنُ شَرُّهُ، وَلاَ يُعْتَقُ مُحَرَّرُهُ‏.‏</big></span></td>
<td valign="top"><strong>ibnmajah 4032</strong>&nbsp; 0.8130<br><br><em><small>⛓ It was narrated from Ibn ‘Umar that the Messenger of Allah (saw) said:</small></em><br><br>“The believer who mixes with people and bears their annoyance with patience will have a greater reward than the believer who does not mix with people and does not put up with their annoyance.”<br><br><span dir="rtl" lang="ar"><big>ـ صلى الله عليه وسلم ـ ‏"‏ الْمُؤْمِنُ الَّذِي يُخَالِطُ النَّاسَ وَيَصْبِرُ عَلَى أَذَاهُمْ أَعْظَمُ أَجْرًا مِنَ الْمُؤْمِنِ الَّذِي لاَ يُخَالِطُ النَّاسَ وَلاَ يَصْبِرُ عَلَى أَذَاهُمْ ‏"‏ ‏.‏</big></span></td>
</tr>
<tr>
<td align="center" valign="top"><strong>5</strong></td>
<td valign="top"><strong>abudawud 4627</strong>&nbsp; 14.8777<br><br>Ibn ‘Umar said: We used to say in the times of the Prophet (saws): We do not compare anyone with Abu Bakr. ’Umar came next and then ‘Uthman. We then would leave (rest of) the companions of the Prophet (saws) without treating any as superior to other.<br><br><span dir="rtl" lang="ar"><big>كُنَّا نَقُولُ فِي زَمَنِ النَّبِيِّ صلى الله عليه وسلم لاَ نَعْدِلُ بِأَبِي بَكْرٍ أَحَدًا ثُمَّ عُمَرَ ثُمَّ عُثْمَانَ ثُمَّ نَتْرُكُ أَصْحَابَ النَّبِيِّ صلى الله عليه وسلم لاَ تَفَاضُلَ بَيْنَهُمْ ‏.‏</big></span></td>
<td valign="top"><strong>riyadussalihin 466</strong>&nbsp; 0.7867<br><br><em><small>⛓ Abu Hurairah (May allah be pleased with him) reported:</small></em><br><br>Messenger of Allah (PBUH) said, "Look at those who are inferior to you and do not look at those who are superior to you, for this will keep you from belittling Allah's favour to you." This is the wording in Sahih Muslim. [Al-Bukhari and Muslim] . The narration in Al-Bukhari is: Messenger of Allah (PBUH) said: "When one of you looks at someone who is superior to him in property and appearance, he should look at someone who is inferior to him".<br><br><span dir="rtl" lang="ar"><big>- وعنه قال‏:‏ قال رسول الله صلى الله عليه وسلم انظروا إلى من هو أسفل منكم ولا تنظروا إلى من هو فوقكم فهو أجدر أن لا تزدروا نعمة الله عليكم‏"‏ ‏(‏‏(‏متفق عليه وهذا لفظ مسلم‏)‏‏)‏‏.‏ وفي رواية البخاري‏:‏ ‏"‏إذا نظر أحدكم إلى من فضل عليه في المال والخلق، فلينظر إلى من هو أسفل منه‏"‏‏.‏ وفي رواية البخاري‏:‏ ‏"‏إذا نظر أحدكم إلى من فضل عليه في المال والخلق، فلينظر إلى من هو أسفل منه‏"‏‏.‏</big></span></td>
<td valign="top"><strong>ibnmajah 4179</strong>&nbsp; 0.8118<br><br><em><small>⛓ It was narrated from ‘Iyad bin Himar that the Prophet (saw) addressed them and said:</small></em><br><br>“Allah has revealed to me that you should be humble towards one another so that none of you boasts to another.”<br><br><span dir="rtl" lang="ar"><big>‏"‏ إِنَّ اللَّهَ عَزَّ وَجَلَّ أَوْحَى إِلَىَّ أَنْ تَوَاضَعُوا حَتَّى لاَ يَفْخَرَ أَحَدٌ عَلَى أَحَدٍ ‏"‏ ‏.‏</big></span></td>
</tr>
<tr>
<td align="center" valign="top"><strong>6</strong></td>
<td valign="top"><strong>bukhari 6557</strong>&nbsp; 14.3854<br><br>Narrated Anas bin Malik: The Prophet said, "Allah will say to the person who will have the minimum punishment in the Fire on the Day of Resurrection, 'If you had things equal to whatever is on the earth, would you ransom yourself (from the punishment) with it?' He will reply, Yes. Allah will say, 'I asked you a much easier thing than this while you were in the backbone of Adam, that is, not to worship others besides Me, but you refused and insisted to worship others besides Me."'<br><br><span dir="rtl" lang="ar"><big>لأَهْوَنِ أَهْلِ النَّارِ عَذَابًا يَوْمَ الْقِيَامَةِ لَوْ أَنَّ لَكَ مَا فِي الأَرْضِ مِنْ شَىْءٍ أَكُنْتَ تَفْتَدِي بِهِ فَيَقُولُ نَعَمْ‏.‏ فَيَقُولُ أَرَدْتُ مِنْكَ أَهْوَنَ مِنْ هَذَا وَأَنْتَ فِي صُلْبِ [name role="nabi"]آدَمَ[/name] أَنْ لاَ تُشْرِكَ بِي شَيْئًا فَأَبَيْتَ إِلاَّ أَنْ تُشْرِكَ بِي ‏"</big></span></td>
<td valign="top"><strong>tirmidhi 2513</strong>&nbsp; 0.7823<br><br><em><small>⛓ Abu Hurairah narrated that the Messenger of Allah (s.a.w) said:</small></em><br><br>"Look to one who is lower than you, and do not look to one who is above you. For indeed that is more worthy(so that you will) not belittle Allah's favors upon you."<br><br><span dir="rtl" lang="ar"><big>صلى الله عليه وسلم ‏"‏ انْظُرُوا إِلَى مَنْ هُوَ أَسْفَلَ مِنْكُمْ وَلاَ تَنْظُرُوا إِلَى مَنْ هُوَ فَوْقَكُمْ فَإِنَّهُ أَجْدَرُ أَنْ لاَ تَزْدَرُوا نِعْمَةَ اللَّهِ عَلَيْكُمْ ‏"‏ ‏.‏ هَذَا حَدِيثٌ صَحِيحٌ ‏.‏</big></span></td>
<td valign="top"><strong>nasai 4725</strong>&nbsp; 0.8065<br><br><em><small>⛓ A similar report was narrated from 'Alqamah bin Wa'il from his father, from the Prophet. Yahya (one of the narrators) said:</small></em><br><br>"He is better than him." [1]<br><br><span dir="rtl" lang="ar"><big>يَحْيَى وَهُوَ أَحْسَنُ مِنْهُ ‏.‏</big></span></td>
</tr>
<tr>
<td align="center" valign="top"><strong>7</strong></td>
<td valign="top"><strong>bukhari 2219</strong>&nbsp; 14.3258<br><br>Narrated Sa`d that his father said: `Abdur-Rahman bin `Auf said to Suhaib, 'Fear Allah and do not ascribe yourself to somebody other than your father.' Suhaib replied, 'I would not like to say it even if I were given large amounts of money, but I say I was kidnapped in my childhood.' "<br><br><span dir="rtl" lang="ar"><big>اتَّقِ اللَّهَ وَلاَ تَدَّعِ إِلَى غَيْرِ أَبِيكَ‏.‏ فَقَالَ صُهَيْبٌ مَا يَسُرُّنِي أَنَّ لِي كَذَا وَكَذَا، وَأَنِّي قُلْتُ ذَلِكَ، وَلَكِنِّي سُرِقْتُ وَأَنَا صَبِيٌّ‏.‏</big></span></td>
<td valign="top"><strong>abudawud 4092</strong>&nbsp; 0.7823<br><br><em><small>⛓ Narrated AbuHurayrah:</small></em><br><br>A man who was beautiful came to the Prophet (saws). He said: Messenger of Allah, I am a man who likes beauty, and I have been given some of it, as you see. And I do not like that anyone excels me (in respect of beauty). Perhaps he said: "even to the extent of thong of my sandal (shirak na'li)", or he he said: "to the extent of strap of my sandal (shis'i na'li)". Is it pride? He replied: No, pride is disdaining what is true and despising people.<br><br><span dir="rtl" lang="ar"><big>يَا رَسُولَ اللَّهِ إِنِّي رَجُلٌ حُبِّبَ إِلَىَّ الْجَمَالُ وَأُعْطِيتُ مِنْهُ مَا تَرَى حَتَّى مَا أُحِبُّ أَنْ يَفُوقَنِي أَحَدٌ - إِمَّا قَالَ بِشِرَاكِ نَعْلِي ‏.‏ وَإِمَّا قَالَ بِشِسْعِ نَعْلِي - أَفَمِنَ الْكِبْرِ ذَلِكَ قَالَ ‏"‏ لاَ وَلَكِنَّ الْكِبْرَ مَنْ بَطَرَ الْحَقَّ وَغَمَطَ النَّاسَ ‏"‏ ‏.‏</big></span></td>
<td valign="top"><strong>ibnmajah 4214</strong>&nbsp; 0.8048<br><br><em><small>⛓ It was narrated from Anas bin Malik that the Messenger of Allah (saw) said:</small></em><br><br>“Allah has revealed to me that you should be humble towards one another and should not wrong one another.”<br><br><span dir="rtl" lang="ar"><big>ـ صلى الله عليه وسلم ـ ‏"‏ إِنَّ اللَّهَ أَوْحَى إِلَىَّ أَنْ تَوَاضَعُوا وَلاَ يَبْغِي بَعْضُكُمْ عَلَى بَعْضٍ ‏"‏ ‏.‏</big></span></td>
</tr>
<tr>
<td align="center" valign="top"><strong>8</strong></td>
<td valign="top"><strong>bukhari 3628</strong>&nbsp; 14.1919<br><br>Narrated Ibn `Abbas: Allah's Apostle in his fatal illness came out, wrapped with a sheet, and his head was wrapped with an oiled bandage. He sat on the pulpit, and praising and glorifying Allah, he said, "Now then, people will increase but the Ansar will decrease in number, so much so that they, compared with the people, will be just like the salt in the meals. So, if any of you should take over the authority by which he can either benefit some people or harm some others, he should accept the goodness of their good people (i.e. Ansar) and excuse the faults of their wrong-doers." That was the l<br><br><span dir="rtl" lang="ar"><big>أَمَّا بَعْدُ فَإِنَّ النَّاسَ يَكْثُرُونَ وَيَقِلُّ الأَنْصَارُ، حَتَّى يَكُونُوا فِي النَّاسِ بِمَنْزِلَةِ الْمِلْحِ فِي الطَّعَامِ، فَمَنْ وَلِيَ مِنْكُمْ شَيْئًا يَضُرُّ فِيهِ قَوْمًا، وَيَنْفَعُ فِيهِ آخَرِينَ، فَلْيَقْبَلْ مِنْ مُحْسِنِهِمْ، وَيَتَجَاوَزْ عَنْ مُسِيئِهِمْ ‏"‏‏.‏ فَكَانَ آخِرَ مَجْلِسٍ جَلَسَ بِهِ النَّبِيُّ صلى الله عليه وسلم‏.‏</big></span></td>
<td valign="top"><strong>muslim 2963 a</strong>&nbsp; 0.7821<br><br><em><small>⛓ Abu Huraira reported that Allah's Messenger (may peace be upon him) said:</small></em><br><br>When one of you looks at one who stands at a higher level than you in regard to wealth and physical structure he should also see one who stands at a lower level than you in regard to these things (in which he stands) at a higher level (as compared to him).<br><br><span dir="rtl" lang="ar"><big>‏"‏ إِذَا نَظَرَ أَحَدُكُمْ إِلَى مَنْ فُضِّلَ عَلَيْهِ فِي الْمَالِ وَالْخَلْقِ فَلْيَنْظُرْ إِلَى مَنْ هُوَ أَسْفَلَ مِنْهُ مِمَّنْ فُضِّلَ عَلَيْهِ ‏"‏ ‏.‏</big></span></td>
<td valign="top"><strong>tirmidhi 1345</strong>&nbsp; 0.8035<br><br><em><small>⛓ Ja'far bin Muhammad narrated from his father: "The Prophet (saws) passed judgement based on an oath along with one witness." He said:</small></em><br><br>"And 'Ali judged between you based on it."<br><br><span dir="rtl" lang="ar"><big>وا لاَ يُقْضَى بِالْيَمِينِ مَعَ الشَّاهِدِ الْوَاحِدِ إِلاَّ فِي الْحُقُوقِ وَالأَمْوَالِ ‏.‏ وَلَمْ يَرَ بَعْضُ أَهْلِ الْعِلْمِ مِنْ أَهْلِ الْكُوفَةِ وَغَيْرِهِمْ أَنْ يُقْضَى بِالْيَمِينِ مَعَ الشَّاهِدِ الْوَاحِدِ ‏.‏</big></span></td>
</tr>
<tr>
<td align="center" valign="top"><strong>9</strong></td>
<td valign="top"><strong>bukhari 3655</strong>&nbsp; 14.0412<br><br>Narrated Ibn `Umar: We used to compare the people as to who was better during the lifetime of Allah's Apostle . We used to regard Abu Bakr as the best, then `Umar, and then `Uthman .<br><br><span dir="rtl" lang="ar"><big>كُنَّا نُخَيِّرُ بَيْنَ النَّاسِ فِي زَمَنِ النَّبِيِّ صلى الله عليه وسلم فَنُخَيِّرُ أَبَا بَكْرٍ، ثُمَّ عُمَرَ بْنَ الْخَطَّابِ، ثُمَّ عُثْمَانَ بْنَ عَفَّانَ رضى الله عنهم‏.‏</big></span></td>
<td valign="top"><strong>adab 898</strong>&nbsp; 0.7815<br><br><em><small>⛓ Ibn 'Abbas said, "</small></em><br><br>I do not know anyone who acts by this ayat: 'Mankind! We created you from a male and a female, and made you into peoples and tribes so that you might come to know each other. The noblest among you in Allah's sight is the one with the most taqwa.' (49:13) One man says to another man, 'I am more noble than you are.' No one is nobler than another person except by taqwa."<br><br><span dir="rtl" lang="ar"><big>الرَّجُلُ لِلرَّجُلِ‏:‏ أَنَا أَكْرَمُ مِنْكَ، فَلَيْسَ أَحَدٌ أَكْرَمَ مِنْ أَحَدٍ إِلا بِتَقْوَى اللهِ‏.‏</big></span></td>
<td valign="top"><strong>ibnmajah 2171</strong>&nbsp; 0.7991<br><br><em><small>⛓ It was narrated from Ibn 'Umar that the Messenger of Allah (SAW) said:</small></em><br><br>"Let one of you not undersell another."[1]<br><br><span dir="rtl" lang="ar"><big>‏"‏ لاَ يَبِيعُ بَعْضُكُمْ عَلَى بَيْعِ بَعْضٍ ‏"‏ ‏.‏</big></span></td>
</tr>
<tr>
<td align="center" valign="top"><strong>10</strong></td>
<td valign="top"><strong>muslim 150 b</strong>&nbsp; 14.0232<br><br>It is narrated on the authority of Sa'd that the Messenger of Allah (may peace be upon him) bestowed upon a group of persons (things), and Sa'd was sitting amongst them. Sa'd said: The Messenger of Allah (may peace be upon him) ignored some of them. And he who was ignored seemed to be more deserving in my eyes (as compared with others). I (Sa'd) said: Messenger of Allah I why is it that you did not give to such and such (man)? Verily I see him a believer. Upon this the Messenger of Allah (may peace be upon him) observed: Or a Muslim? I kept quiet for some time but I was again impelled (to expr<br><br><span dir="rtl" lang="ar"><big>صلى الله عليه وسلم ‏"‏ أَوْ مُسْلِمًا ‏.‏ إِنِّي لأُعْطِي الرَّجُلَ وَغَيْرُهُ أَحَبُّ إِلَىَّ مِنْهُ خَشْيَةَ أَنْ يُكَبَّ فِي النَّارِ عَلَى وَجْهِهِ ‏"‏ ‏.‏</big></span></td>
<td valign="top"><strong>muslim 2536</strong>&nbsp; 0.7795<br><br><em><small>⛓ 'A'isha reported that a person asked Allah's Apostle (may peace be upon him) as to who amongst the people were the best. He said:</small></em><br><br>Of the generation to which I belong, then of the second generation (generation adjacent to my generation), then of the third generation (generation adjacent to the second generation).<br><br><span dir="rtl" lang="ar"><big>‏"‏ الْقَرْنُ الَّذِي أَنَا فِيهِ ثُمَّ الثَّانِي ثُمَّ الثَّالِثُ ‏"‏ ‏.‏</big></span></td>
<td valign="top"><strong>bulugh 1438</strong>&nbsp; 0.7975<br><br><em><small>⛓ Abu Hurairah (RAA) narrated that the Messenger of Allah (P.B.U.H.) said, “</small></em><br><br>Look at those who are lower than you (financially) but do not look at those who are higher than you, lest you belittle the favors Allah conferred upon you.” Agreed upon.</td>
</tr>
</tbody></table>

## English OpenAI

<table width="100%"><thead><tr>
<th width="4%">#</th>
<th width="48%">English OpenAI small (clean matn)</th>
<th width="48%">English OpenAI large (clean matn)</th>
</tr></thead><tbody>
<tr>
<td align="center" valign="top"><strong>1</strong></td>
<td valign="top"><strong>adab 328</strong>&nbsp; 0.7196<br><br>Ibn 'Abbas said, "When you want to mention your companion's faults, remember your own faults."<br><br><span dir="rtl" lang="ar"><big>‏:‏ إِذَا أَرَدْتَ أَنْ تَذْكُرَ عُيُوبَ صَاحِبِكَ، فَاذْكُرْ عُيُوبَ نَفْسِكَ‏.‏</big></span></td>
<td valign="top"><strong>tirmidhi 1554</strong>&nbsp; 0.5818<br><br><span dir="rtl" lang="ar"><big>اَ حَدَّثَنَا سُلَيْمُ بْنُ أَخْضَرَ، عَنْ عُبَيْدِ اللَّهِ بْنِ عُمَرَ، عَنْ نَافِعٍ، عَنِ ابْنِ عُمَرَ، أَنَّ رَسُولَ اللَّهِ صلى الله عليه وسلم قَسَمَ فِي النَّفَلِ لِلْفَرَسِ بِسَهْمَيْنِ وَلِلرَّجُلِ بِسَهْمٍ ‏.‏</big></span></td>
</tr>
<tr>
<td align="center" valign="top"><strong>2</strong></td>
<td valign="top"><strong>muslim 7068</strong>&nbsp; 0.7168<br><br>Abu Huraira reported that Allah's Messenger (may peace be upon him) said: When one of you looks at one who stands at a higher level than you in regard to wealth and physical structure he should also see one who stands at a lower level than you in regard to these things (in which he stands) at a higher level (as compared to him).</td>
<td valign="top"><strong>tirmidhi 1561</strong>&nbsp; 0.5818<br><br><span dir="rtl" lang="ar"><big>الْبُخَارِيُّ لاَ يَصِّحُ حَدِيثُ سُلَيْمَانَ بْنِ مُوسَى إِنَّمَا رَوَاهُ دَاوُدُ بْنُ عَمْرٍو عَنْ أَبِي سَلاَّمٍ عَنِ النَّبِيِّ صلى الله عليه وسلم مُرْسَلاً وَسُلَيْمَانُ بْنُ مُوسَى مُنْكَرُ الْحَدِيثِ أَنَا لاَ أَرْوِي عَنْهُ شَيْئًا رَوَى أَحَادِيثَ مُنْكَرَةً عَامَّتُهَا مِنْهَا حَدِيثُ نَافِعٍ عَنِ ابْنِ عُمَرَ أَنَّ النَّبِيَّ صلى الله عليه وسلم كُفِّنَ فِي ثَلاَثَةِ أَثْوَابٍ ‏.‏ وَحَدِ</big></span></td>
</tr>
<tr>
<td align="center" valign="top"><strong>3</strong></td>
<td valign="top"><strong>riyadussalihin 466</strong>&nbsp; 0.6910<br><br>Abu Hurairah (May allah be pleased with him) reported: Messenger of Allah (PBUH) said, "Look at those who are inferior to you and do not look at those who are superior to you, for this will keep you from belittling Allah's favour to you." This is the wording in Sahih Muslim. [Al-Bukhari and Muslim] . The narration in Al-Bukhari is: Messenger of Allah (PBUH) said: "When one of you looks at someone who is superior to him in property and appearance, he should look at someone who is inferior to him".<br><br><span dir="rtl" lang="ar"><big>- وعنه قال‏:‏ قال رسول الله صلى الله عليه وسلم انظروا إلى من هو أسفل منكم ولا تنظروا إلى من هو فوقكم فهو أجدر أن لا تزدروا نعمة الله عليكم‏"‏ ‏(‏‏(‏متفق عليه وهذا لفظ مسلم‏)‏‏)‏‏.‏ وفي رواية البخاري‏:‏ ‏"‏إذا نظر أحدكم إلى من فضل عليه في المال والخلق، فلينظر إلى من هو أسفل منه‏"‏‏.‏ وفي رواية البخاري‏:‏ ‏"‏إذا نظر أحدكم إلى من فضل عليه في المال والخلق، فلينظر إلى من هو أسفل منه‏"‏‏.‏</big></span></td>
<td valign="top"><strong>tirmidhi 1705</strong>&nbsp; 0.5818<br><br><span dir="rtl" lang="ar"><big>‏"‏ أَلاَ كُلُّكُمْ رَاعٍ وَكُلُّكُمْ مَسْئُولٌ عَنْ رَعِيَّتِهِ فَالأَمِيرُ الَّذِي عَلَى النَّاسِ رَاعٍ وَمَسْئُولٌ عَنْ رَعِيَّتِهِ وَالرَّجُلُ رَاعٍ عَلَى أَهْلِ بَيْتِهِ وَهُوَ مَسْئُولٌ عَنْهُمْ وَالْمَرْأَةُ رَاعِيَةٌ عَلَى بَيْتِ بَعْلِهَا وَهِيَ مَسْئُولَةٌ عَنْهُ وَالْعَبْدُ رَاعٍ عَلَى مَالِ سَيِّدِهِ وَهُوَ مَسْئُولٌ عَنْهُ أَلاَ فَكُلُّكُمْ رَاعٍ وَكُلُّكُمْ مَسْئُولٌ عَنْ رَعِيَّتِهِ</big></span></td>
</tr>
<tr>
<td align="center" valign="top"><strong>4</strong></td>
<td valign="top"><strong>ibnmajah 2171</strong>&nbsp; 0.6830<br><br>It was narrated from Ibn 'Umar that the Messenger of Allah (SAW) said: "Let one of you not undersell another."[1]<br><br><span dir="rtl" lang="ar"><big>‏"‏ لاَ يَبِيعُ بَعْضُكُمْ عَلَى بَيْعِ بَعْضٍ ‏"‏ ‏.‏</big></span></td>
<td valign="top"><strong>tirmidhi 1709</strong>&nbsp; 0.5818<br><br><span dir="rtl" lang="ar"><big>هَذَا أَصَحُّ مِنْ حَدِيثِ قُطْبَةَ ‏.‏</big></span></td>
</tr>
<tr>
<td align="center" valign="top"><strong>5</strong></td>
<td valign="top"><strong>muslim 6696</strong>&nbsp; 0.6823<br><br>Ibn Umar reported Allah's Apostle (may peace be upon him) as saying: The similitude of a hypocrite is that of a sheep which roams aimlessly between two flocks. She goes to one at one time and to the other at another time.</td>
<td valign="top"><strong>bukhari 352</strong>&nbsp; 0.5818<br><br><span dir="rtl" lang="ar"><big>إِنَّمَا صَنَعْتُ ذَلِكَ لِيَرَانِي أَحْمَقُ مِثْلُكَ، وَأَيُّنَا كَانَ لَهُ ثَوْبَانِ عَلَى عَهْدِ النَّبِيِّ صلى الله عليه وسلم</big></span></td>
</tr>
<tr>
<td align="center" valign="top"><strong>6</strong></td>
<td valign="top"><strong>bulugh 1482</strong>&nbsp; 0.6816<br><br>Abu Hurairah (RAA) narrated that the Messenger of Allah (P.B.U.H.) said, “Look at those who are lower than you (financially) but do not look at those who are higher than you, lest you belittle the favors Allah conferred upon you.” Agreed upon.</td>
<td valign="top"><strong>bukhari 211</strong>&nbsp; 0.5818<br><br><span dir="rtl" lang="ar"><big>شَرِبَ لَبَنًا، فَمَضْمَضَ وَقَالَ ‏"‏ إِنَّ لَهُ دَسَمًا ‏"</big></span></td>
</tr>
<tr>
<td align="center" valign="top"><strong>7</strong></td>
<td valign="top"><strong>adab 592</strong>&nbsp; 0.6805<br><br>Abu Hurayra said, "One of you looks at the mote in his brother's eye while forgetting the stump in his own eye."<br><br><span dir="rtl" lang="ar"><big>‏:‏ يُبْصِرُ أَحَدُكُمُ الْقَذَاةَ فِي عَيْنِ أَخِيهِ، وَيَنْسَى الْجِذْلَ، أَوِ الْجِذْعَ، فِي عَيْنِ نَفْسِهِ‏.‏</big></span></td>
<td valign="top"><strong>nasai 2683</strong>&nbsp; 0.5818<br><br><span dir="rtl" lang="ar"><big>رَأَيْتُ رَسُولَ اللَّهِ صلى الله عليه وسلم يُهِلُّ مُلَبِّدًا ‏.‏</big></span></td>
</tr>
<tr>
<td align="center" valign="top"><strong>8</strong></td>
<td valign="top"><strong>bukhari 497</strong>&nbsp; 0.6798<br><br>Narrated Abu Huraira: Allah's Apostle said, "If anyone of you looked at a person who was made superior to him in property and (in good) appearance, then he should also look at the one who is inferior to him.<br><br><span dir="rtl" lang="ar"><big>كَانَ جِدَارُ الْمَسْجِدِ عِنْدَ الْمِنْبَرِ مَا كَادَتِ الشَّاةُ تَجُوزُهَا‏.‏</big></span></td>
<td valign="top"><strong>nasai 2872</strong>&nbsp; 0.5818<br><br><span dir="rtl" lang="ar"><big>جَابِرٌ قَدِمَ النَّبِيُّ صلى الله عليه وسلم مَكَّةَ صَبِيحَةَ رَابِعَةٍ مَضَتْ مِنْ ذِي الْحِجَّةِ ‏.‏</big></span></td>
</tr>
<tr>
<td align="center" valign="top"><strong>9</strong></td>
<td valign="top"><strong>tirmidhi 2513</strong>&nbsp; 0.6766<br><br>Abu Hurairah narrated that the Messenger of Allah (s.a.w) said: "Look to one who is lower than you, and do not look to one who is above you. For indeed that is more worthy(so that you will) not belittle Allah's favors upon you."<br><br><span dir="rtl" lang="ar"><big>صلى الله عليه وسلم ‏"‏ انْظُرُوا إِلَى مَنْ هُوَ أَسْفَلَ مِنْكُمْ وَلاَ تَنْظُرُوا إِلَى مَنْ هُوَ فَوْقَكُمْ فَإِنَّهُ أَجْدَرُ أَنْ لاَ تَزْدَرُوا نِعْمَةَ اللَّهِ عَلَيْكُمْ ‏"‏ ‏.‏ هَذَا حَدِيثٌ صَحِيحٌ ‏.‏</big></span></td>
<td valign="top"><strong>riyadussalihin 1763</strong>&nbsp; 0.5818<br><br><span dir="rtl" lang="ar"><big>- وعن أم المؤمنين جويرة بنت الحارس رضي الله عنها أن النبي صلى الله عليه وسلم دخل عليها يوم الجمعة وهي صائمة، فقال‏:‏ ‏"‏ أصمت أمس‏؟‏‏"‏ قالت‏:‏ لا، قال‏:‏ ‏"‏ تريدين أن تصومي غدا ‏"‏ قالت‏:‏ لا، قال ‏:‏ ‏"‏فأفطري‏"‏ ‏(‏‏(‏رواه البخاري‏)‏‏)‏</big></span></td>
</tr>
<tr>
<td align="center" valign="top"><strong>10</strong></td>
<td valign="top"><strong>bulugh 1514</strong>&nbsp; 0.6764<br><br>Ibn ’Umar (RAA) narrated that the Messenger of Allah (P.B.U.H.) said, “He who imitates any people (in their actions) is considered to be one of them.” Related by Abu Dawud and Ibn Hibban graded it as Sahih.</td>
<td valign="top"><strong>shamail 67</strong>&nbsp; 0.5818<br><br><span dir="rtl" lang="ar"><big>تْ‏:‏ رَأَيْتُ النَّبِيَّ صلى الله عليه وسلم وَعَلَيْهِ أَسْمَالُ مُلَيَّتَيْنِ، كَانَتَا بِزَعْفَرَانٍ، وَقَدْ نَفَضَتْهُ وَفِي الْحَدِيثِ قِصَّةٌ طَوِيلَةٌ‏.‏</big></span></td>
</tr>
</tbody></table>

## Arabic / Multilingual OpenAI

<table width="100%"><thead><tr>
<th width="4%">#</th>
<th width="19%">Arabic OpenAI (small)</th>
<th width="19%">Arabic OpenAI (large)</th>
<th width="19%">E5 Multilingual</th>
<th width="19%">BGE-M3</th>
<th width="19%">Qwen3-Embed</th>
</tr></thead><tbody>
<tr>
<td align="center" valign="top"><strong>1</strong></td>
<td valign="top"><strong>ibnmajah 1977</strong>&nbsp; 0.6539<br><br><em><small>⛓ It was narrated from Ibn 'Abbas that:</small></em><br><br>the Prophet said: "The best of you is the one who is best to his wife, and I am the best of you to my wives."<br><br><span dir="rtl" lang="ar"><big>‏"‏ خَيْرُكُمْ خَيْرُكُمْ لأَهْلِهِ وَأَنَا خَيْرُكُمْ لأَهْلِي ‏"‏ ‏.‏</big></span></td>
<td valign="top"><strong>muslim 2963 a</strong>&nbsp; 0.6747<br><br><em><small>⛓ Abu Huraira reported that Allah's Messenger (may peace be upon him) said:</small></em><br><br>When one of you looks at one who stands at a higher level than you in regard to wealth and physical structure he should also see one who stands at a lower level than you in regard to these things (in which he stands) at a higher level (as compared to him).<br><br><span dir="rtl" lang="ar"><big>‏"‏ إِذَا نَظَرَ أَحَدُكُمْ إِلَى مَنْ فُضِّلَ عَلَيْهِ فِي الْمَالِ وَالْخَلْقِ فَلْيَنْظُرْ إِلَى مَنْ هُوَ أَسْفَلَ مِنْهُ مِمَّنْ فُضِّلَ عَلَيْهِ ‏"‏ ‏.‏</big></span></td>
<td valign="top"><strong>ibnabishayba </strong>&nbsp; 0.9205<br><br><span dir="rtl" lang="ar"><big>" تَعْتَدُّ مِنْ آخِرِ طَلَاقِهَا "</big></span></td>
<td valign="top"><em>ERROR: HTTP Error 404: NOT FOUND</em></td>
<td valign="top"><em>ERROR: HTTP Error 500: INTERNAL SERVER ERROR</em></td>
</tr>
<tr>
<td align="center" valign="top"><strong>2</strong></td>
<td valign="top"><strong>abudawud 879</strong>&nbsp; 0.6477<br><br>A’ishah said; one night I missed the Messenger of Allah (may peace be upon him) and when I sought him on the spot of prayer I found him in prostration with his feet raised, and he was saying:”(O Allah), I seek refuge in Your good pleasure from Your anger, and in Your Mercy from Your Punishment, and I seek refuge from You in You; I am not able to praise You (the way that You deserve to be praised), for You are as You have praised Yourself”.<br><br><span dir="rtl" lang="ar"><big>‏"‏ أَعُوذُ بِرِضَاكَ مِنْ سَخَطِكَ وَأَعُوذُ بِمُعَافَاتِكَ مِنْ عُقُوبَتِكَ وَأَعُوذُ بِكَ مِنْكَ لاَ أُحْصِي ثَنَاءً عَلَيْكَ أَنْتَ كَمَا أَثْنَيْتَ عَلَى نَفْسِكَ ‏"‏ ‏.‏</big></span></td>
<td valign="top"><strong>ibnhibban </strong>&nbsp; 0.6713<br><br><span dir="rtl" lang="ar"><big>" إِذَا رَأَى أَحَدُكُمْ مَنْ فُضِّلَ عَلَيْهِ فِي الْخَلْقِ ، أَوِ الرِّزْقِ ، فَلْيَنْظُرْ إِلَى مَنْ هُوَ أَسْفَلُ مِنْهُ مِمَّنْ فُضِّلَ هُوَ عَلَيْهِ "</big></span></td>
<td valign="top"><strong>adab </strong>&nbsp; 0.9204<br><br><span dir="rtl" lang="ar"><big>‏:‏ خِيَارُكُمْ أَحَاسِنُكُمْ أَخْلاَقًا‏.‏</big></span></td>
<td valign="top"><em>ERROR: HTTP Error 404: NOT FOUND</em></td>
<td valign="top"><em>ERROR: HTTP Error 500: INTERNAL SERVER ERROR</em></td>
</tr>
<tr>
<td align="center" valign="top"><strong>3</strong></td>
<td valign="top"><strong>nasai 1130</strong>&nbsp; 0.6473<br><br><em><small>⛓ It was narrated that 'Aishah said:</small></em><br><br>"I noticed the Messenger of Allah (SAW) was missing one night and I found him prostrating with the tops of his feet facing toward the Qiblah. I heard him saying: 'A'udhu biridaka min sakhatika, wa a'udhu bimu 'afatika min 'uqubatika wa a'udhu bika minka la uhsi thana'an 'alaika anta kama athnaita 'ala nafsik (I seek refuge in Your pleasure from Your wrath; I seek refuge in Your forgiveness from Your punishment; I seek refuge in You from You. I cannot praise You enough, You are as You have praised Yourself.)"<br><br><span dir="rtl" lang="ar"><big>‏"‏ أَعُوذُ بِرِضَاكَ مِنْ سَخَطِكَ وَأَعُوذُ بِمُعَافَاتِكَ مِنْ عُقُوبَتِكَ وَأَعُوذُ بِكَ مِنْكَ لاَ أُحْصِي ثَنَاءً عَلَيْكَ أَنْتَ كَمَا أَثْنَيْتَ عَلَى نَفْسِكَ ‏"‏ ‏.‏</big></span></td>
<td valign="top"><strong>ibnhibban </strong>&nbsp; 0.6713<br><br><span dir="rtl" lang="ar"><big>" إِذَا نَظَرَ أَحَدُكُمْ إِلَى مَنْ فُضِّلَ عَلَيْهِ فِي الْمَالِ وَالْخَلْقِ ، فَلْيَنْظُرْ إِلَى مَنْ هُوَ أَسْفَلُ مِنْهُ مِمَّنْ فُضِّلَ هُوَ عَلَيْهِ "</big></span></td>
<td valign="top"><strong>ibnabishayba </strong>&nbsp; 0.9201<br><br><span dir="rtl" lang="ar"><big>"</big></span></td>
<td valign="top"><em>ERROR: HTTP Error 404: NOT FOUND</em></td>
<td valign="top"><em>ERROR: HTTP Error 500: INTERNAL SERVER ERROR</em></td>
</tr>
<tr>
<td align="center" valign="top"><strong>4</strong></td>
<td valign="top"><strong>nasai 169</strong>&nbsp; 0.6471<br><br><em><small>⛓ It was narrated from Abu Hurairah that 'Aishah said:</small></em><br><br>"I noticed the Prophet (PBUH) was not there one night, so I started looking for him with my hand. My hand touched his feet and they were held upright, and he was prostrating and saying: 'I seek refuge in Your pleasure from Your anger, in Your forgiveness from Your punishment, and I seek refuge in You from You. I cannot praise You enough, You are as You have praised yourself.'"<br><br><span dir="rtl" lang="ar"><big>‏"‏ أَعُوذُ بِرِضَاكَ مِنْ سَخَطِكَ وَبِمُعَافَاتِكَ مِنْ عُقُوبَتِكَ وَأَعُوذُ بِكَ مِنْكَ لاَ أُحْصِي ثَنَاءً عَلَيْكَ أَنْتَ كَمَا أَثْنَيْتَ عَلَى نَفْسِكَ ‏"‏ ‏.‏</big></span></td>
<td valign="top"><strong>ibnhibban </strong>&nbsp; 0.6688<br><br><span dir="rtl" lang="ar"><big>" إِذَا رَأَى أَحَدُكُمْ مَنْ فَوْقَهُ فِي الْمَالِ وَالْحَسَبِ ، فَلْيَنْظُرْ إِلَى مَنْ هُوَ دُونَهُ فِي الْمَالِ وَالْحَسَبِ "</big></span></td>
<td valign="top"><strong>ibnkhuzayma </strong>&nbsp; 0.9200<br><br><span dir="rtl" lang="ar"><big>" الْتَمِسُوهَا فِي الْعَشْرِ الأَوَاخِرِ "</big></span></td>
<td valign="top"><em>ERROR: HTTP Error 404: NOT FOUND</em></td>
<td valign="top"><em>ERROR: HTTP Error 500: INTERNAL SERVER ERROR</em></td>
</tr>
<tr>
<td align="center" valign="top"><strong>5</strong></td>
<td valign="top"><strong>muslim 19 b</strong>&nbsp; 0.6386<br><br>The above hadith has been mentioned with a different chain with a slightly different wording at the beginning, then follows the same.<br><br><span dir="rtl" lang="ar"><big>‏"‏ إِنَّكَ سَتَأْتِي قَوْمًا ‏"‏ بِمِثْلِ حَدِيثِ وَكِيعٍ ‏.‏</big></span></td>
<td valign="top"><strong>bukhari 6490</strong>&nbsp; 0.6672<br><br><em><small>⛓ Narrated Abu Huraira:</small></em><br><br>Allah's Apostle said, "If anyone of you looked at a person who was made superior to him in property and (in good) appearance, then he should also look at the one who is inferior to him.<br><br><span dir="rtl" lang="ar"><big>إِذَا نَظَرَ أَحَدُكُمْ إِلَى مَنْ فُضِّلَ عَلَيْهِ فِي الْمَالِ وَالْخَلْقِ، فَلْيَنْظُرْ إِلَى مَنْ هُوَ أَسْفَلَ مِنْهُ ‏"</big></span></td>
<td valign="top"><strong>abdurrazzaq </strong>&nbsp; 0.9197<br><br><span dir="rtl" lang="ar"><big>الْحَجَرَ بَعْضُهُ مِنَ الْبَيْتِ</big></span></td>
<td valign="top"><em>ERROR: HTTP Error 404: NOT FOUND</em></td>
<td valign="top"><em>ERROR: HTTP Error 500: INTERNAL SERVER ERROR</em></td>
</tr>
<tr>
<td align="center" valign="top"><strong>6</strong></td>
<td valign="top"><strong>nasai 813</strong>&nbsp; 0.6360<br><br><em><small>⛓ It was narrated from Anas that the Prophet (saws) used to say:</small></em><br><br>"Make your rows straight, make your rows straight, make your rows straight. By the One in Whose Hand is my soul! I can see you behind me as I can see you in front of me."<br><br><span dir="rtl" lang="ar"><big>‏"‏ اسْتَوُوا اسْتَوُوا اسْتَوُوا فَوَالَّذِي نَفْسِي بِيَدِهِ إِنِّي لأَرَاكُمْ مِنْ خَلْفِي كَمَا أَرَاكُمْ مِنْ بَيْنِ يَدَىَّ ‏"‏ ‏.‏</big></span></td>
<td valign="top"><strong>tirmidhi 1780</strong>&nbsp; 0.6603<br><br><em><small>⛓ Narrated 'Aishah:</small></em><br><br>"The Messenger of Allah (saws) said to me: 'If you want to stick with me, then suffice yourself in the world with the provisions of the rider. And beware of gatherings of the rich, and do not consider a garment to be worn out until it has been patched.'" [Abu 'Eisa said:] This Hadith is Gharib, we do not know of it except as a narration of Salih bin Hassan. He said: I heard Muhammad bin Isma'il saying: "Salih bin Hassan is Munkar is Hadith." And Salih bin Hassan - the one who Ibn Abi Dhi'b reports from - is trustworthy. [Abu 'Eisa said:] The meaning of this saying: "And beware of gathering of <br><br><span dir="rtl" lang="ar"><big>‏"‏ مَنْ رَأَى مَنْ فُضِّلَ عَلَيْهِ فِي الْخَلْقِ وَالرِّزْقِ فَلْيَنْظُرْ إِلَى مَنْ هُوَ أَسْفَلُ مِنْهُ مِمَّنْ فُضِّلَ هُوَ عَلَيْهِ فَإِنَّهُ أَجْدَرُ أَنْ لاَ يَزْدَرِيَ نِعْمَةَ اللَّهِ عَلَيْهِ ‏"‏ ‏.‏ وَيُرْوَى عَنْ عَوْنِ بْنِ عَبْدِ اللَّهِ بْنِ عُتْبَةَ قَالَ صَحِبْتُ الأَغْنِيَاءَ فَلَمْ أَرَ أَحَدًا أَكْثَرَ هَمًّا مِنِّي أَرَى دَابَّةً خَيْرًا مِنْ دَابَّتِي وَثَوْبًا خَيْرًا مِنْ </big></span></td>
<td valign="top"><strong>ibnhibban </strong>&nbsp; 0.9193<br><br><span dir="rtl" lang="ar"><big>" سَاقِي الْقَوْمِ آخِرُهُمْ "</big></span></td>
<td valign="top"><em>ERROR: HTTP Error 404: NOT FOUND</em></td>
<td valign="top"><em>ERROR: HTTP Error 500: INTERNAL SERVER ERROR</em></td>
</tr>
<tr>
<td align="center" valign="top"><strong>7</strong></td>
<td valign="top"><strong>adab 942</strong>&nbsp; 0.6349<br><br><em><small>⛓ Abu Hurayra reported that the Prophet, may Allah bless him and grant him peace, said, "</small></em><br><br>When one of you yawns, he should repress it as much as possible."<br><br><span dir="rtl" lang="ar"><big>‏:‏ إِذَا تَثَاءَبَ أَحَدُكُمْ فَلْيَكْظِمْ مَا اسْتَطَاعَ‏.‏</big></span></td>
<td valign="top"><strong>ibnkhuzayma </strong>&nbsp; 0.6508<br><br><span dir="rtl" lang="ar"><big>الأَعْمَالَ تَتَبَاهَى ، فَتَقُولُ الصَّدَقَةُ أَنَا أَفْضَلُكُمْ "</big></span></td>
<td valign="top"><strong>abdurrazzaq </strong>&nbsp; 0.9183<br><br><span dir="rtl" lang="ar"><big>جَلَدَتْ أَمَةً لَهَا</big></span></td>
<td valign="top"><em>ERROR: HTTP Error 404: NOT FOUND</em></td>
<td valign="top"><em>ERROR: HTTP Error 500: INTERNAL SERVER ERROR</em></td>
</tr>
<tr>
<td align="center" valign="top"><strong>8</strong></td>
<td valign="top"><strong>ahmad 1398</strong>&nbsp; 0.6331<br><br><em><small>⛓ It was narrated from Moosa bin Talhah, from his father, that The Prophet (ﷺ) said:</small></em><br><br>“Let one of you put something in front of him the height of the back of a saddle, then pray.`<br><br><span dir="rtl" lang="ar"><big>يَجْعَلُ أَحَدُكُمْ بَيْنَ يَدَيْهِ مِثْلَ مُؤْخِرَةِ الرَّحْلِ ثُمَّ يُصَلِّي‏.‏</big></span></td>
<td valign="top"><strong>ibnabishayba </strong>&nbsp; 0.6494<br><br><span dir="rtl" lang="ar"><big>" لَا حَسَدَ إِلَّا فِي اثْنَتَيْنِ : رَجُلٍ آتَاهُ اللَّهُ الْقُرْآنَ فَهُوَ يَتْلُوهُ آنَاءَ اللَّيْلِ وَآنَاءَ النَّهَارِ , فَيَقُولُ الرَّجُلُ : لَوْ آتَانِي اللَّهُ مثل مَا آتَى فُلَانًا فَعَلْتُ مثل مَا يَفْعَلُ , وَرَجُلٍ آتَاهُ اللَّهُ مَالًا فَهُوَ يُنْفِقُهُ فِي حَقِّهِ فَيَقُولُ الرَّجُلُ : لَوْ آتَانِي اللَّهُ مثل مَا آتَى فُلَانًا فَعَلْتُ مثل مَا يَفْعَلُ "</big></span></td>
<td valign="top"><strong>abdurrazzaq </strong>&nbsp; 0.9178<br><br><span dir="rtl" lang="ar"><big>كَفِّرْ عَنْ يَمِينِكَ</big></span></td>
<td valign="top"><em>ERROR: HTTP Error 404: NOT FOUND</em></td>
<td valign="top"><em>ERROR: HTTP Error 500: INTERNAL SERVER ERROR</em></td>
</tr>
<tr>
<td align="center" valign="top"><strong>9</strong></td>
<td valign="top"><strong>nasai 3782</strong>&nbsp; 0.6331<br><br><em><small>⛓ It was narrated from 'Abdur-Rahman bin Samurah that the Messenger of Allah said:</small></em><br><br>"If any one of you swears an oath, then he sees something better than it, let him offer expiation for his oath, and look at what is better and do it."<br><br><span dir="rtl" lang="ar"><big>‏"‏ إِذَا حَلَفَ أَحَدُكُمْ عَلَى يَمِينٍ فَرَأَى غَيْرَهَا خَيْرًا مِنْهَا فَلْيُكَفِّرْ عَنْ يَمِينِهِ وَلْيَنْظُرِ الَّذِي هُوَ خَيْرٌ فَلْيَأْتِهِ ‏"‏ ‏.‏</big></span></td>
<td valign="top"><strong>abudawud 1663</strong>&nbsp; 0.6412<br><br>Abu Sa’id al-Khudri said While we were traveling along with the Messenger of Allah (saws) a man came to him on his she camel, and began to drive her right and left. The Messenger of Allah (saws) said he who has a spare riding beast should give it to him who has no riding beast; and he who has surplus equipment should give it to who has no equipment. We thought that none of us had a right in surplus property.<br><br><span dir="rtl" lang="ar"><big>صلى الله عليه وسلم ‏"‏ مَنْ كَانَ عِنْدَهُ فَضْلُ ظَهْرٍ فَلْيَعُدْ بِهِ عَلَى مَنْ لاَ ظَهْرَ لَهُ وَمَنْ كَانَ عِنْدَهُ فَضْلُ زَادٍ فَلْيَعُدْ بِهِ عَلَى مَنْ لاَ زَادَ لَهُ ‏"‏ ‏.‏ حَتَّى ظَنَنَّا أَنَّهُ لاَ حَقَّ لأَحَدٍ مِنَّا فِي الْفَضْلِ ‏.‏</big></span></td>
<td valign="top"><strong>abdurrazzaq </strong>&nbsp; 0.9174<br><br><span dir="rtl" lang="ar"><big>يَصُومُ الْمُجَاوِرُ</big></span></td>
<td valign="top"><em>ERROR: HTTP Error 404: NOT FOUND</em></td>
<td valign="top"><em>ERROR: HTTP Error 500: INTERNAL SERVER ERROR</em></td>
</tr>
<tr>
<td align="center" valign="top"><strong>10</strong></td>
<td valign="top"><strong>muslim 632 b</strong>&nbsp; 0.6328<br><br><em><small>⛓ Abu Huraira reported Allah's Messenger (may peace be upon him) as saying:</small></em><br><br>Angels take turns among you by night and by day, and the rest of the hadith is the same.<br><br><span dir="rtl" lang="ar"><big>‏"‏ وَالْمَلاَئِكَةُ يَتَعَاقَبُونَ فِيكُمْ ‏"‏ ‏.‏ بِمِثْلِ حَدِيثِ أَبِي الزِّنَادِ ‏.‏</big></span></td>
<td valign="top"><strong>bukhari 5026</strong>&nbsp; 0.6409<br><br><em><small>⛓ Narrated Abu Huraira:</small></em><br><br>Allah's Apostle I said, "Not to wish to be the like of except two men: A man whom Allah has taught the Qur'an and he recites it during the hours of the night and during the hours of the day, and his neighbor listens to him and says, 'I wish I had been given what has been given to so-and-so, so that I might do what he does; and a man whom Allah has given wealth and he spends it on what is just and right, whereupon an other man May say, 'I wish I had been given what so-and-so has been given, for then I would do what he does."<br><br><span dir="rtl" lang="ar"><big>لاَ حَسَدَ إِلاَّ فِي اثْنَتَيْنِ رَجُلٌ عَلَّمَهُ اللَّهُ الْقُرْآنَ فَهُوَ يَتْلُوهُ آنَاءَ اللَّيْلِ وَآنَاءَ النَّهَارِ فَسَمِعَهُ جَارٌ لَهُ فَقَالَ لَيْتَنِي أُوتِيتُ مِثْلَ مَا أُوتِيَ فُلاَنٌ فَعَمِلْتُ مِثْلَ مَا يَعْمَلُ، وَرَجُلٌ آتَاهُ اللَّهُ مَالاً فَهْوَ يُهْلِكُهُ فِي الْحَقِّ فَقَالَ رَجُلٌ لَيْتَنِي أُوتِيتُ مِثْلَ مَا أُوتِيَ فُلاَنٌ فَعَمِلْتُ مِثْلَ مَا يَعْمَلُ ‏"‏‏.‏</big></span></td>
<td valign="top"><strong>ibnabishayba </strong>&nbsp; 0.9171<br><br><span dir="rtl" lang="ar"><big>" يَسْجُدُ فِي الْآخِرَةِ "</big></span></td>
<td valign="top"><em>ERROR: HTTP Error 404: NOT FOUND</em></td>
<td valign="top"><em>ERROR: HTTP Error 500: INTERNAL SERVER ERROR</em></td>
</tr>
</tbody></table>

---

*Generated by `tests/focused_comparison.py` · pool=50 · N=10*