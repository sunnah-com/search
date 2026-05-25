# Search Quality Report
**Query:** "comparing yourself to others"  
**Date:** 2026-05-20  
**Modes tested:** lexical · hybrid · semantic  
**Models tested:** openai-small-en · openai-small-multi · nomic · mxbai  
**Results per case:** top 10 · semantic sections re-fetched with size=100 (matches production PHP behavior)

---

## Models

| Key | Full name | Params | Dimensions | Context | Provider | Cost | Index coverage |
|---|---|---|---|---|---|---|---|
| `openai-small-en` | text-embedding-3-small | Undisclosed | 1536 | 8191 tokens | OpenAI API | Per token (~$0.02/1M) | English only (~48k docs) |
| `openai-small-multi` | text-embedding-3-small | Undisclosed | 1536 | 8191 tokens | OpenAI API | Per token (~$0.02/1M) | English + Arabic (~180k docs) |
| `nomic` | nomic-embed-text-v1.5 | ~137M | 768 | 8192 tokens | Nomic AI — runs locally via Ollama | Free | English only (~48k docs) |
| `mxbai` | mxbai-embed-large-v1 | ~335M | 1024 | 512 tokens | mixedbread.ai — runs locally via Ollama | Free | English only (~48k docs) |

**openai-small-en / openai-small-multi** — the same underlying OpenAI model (`text-embedding-3-small`), but indexed against different datasets. The `-en` variant embeds only English hadiths; the `-multi` variant embeds all English + Arabic hadiths (~180k total) so multilingual queries can surface Arabic-language results. Parameter count isn't published by OpenAI. Generally strong for English semantic matching.

**nomic** (`nomic-embed-text-v1.5`) — 137M-parameter open-source model by Nomic AI. Standout feature: 8192-token context window, the longest of the four models, so even very long hadiths are embedded without truncation. Apache 2.0 licensed. Runs entirely locally via Ollama — no API cost, no data leaves the machine.

**mxbai** (`mxbai-embed-large-v1`) — 335M-parameter model by mixedbread.ai, based on BERT-large architecture. The largest and most capable local model tested. The key trade-off: a short 512-token context window means longer hadiths get silently truncated at indexing time, which may affect recall on longer texts. Apache 2.0 licensed. Runs locally via Ollama.

---

## LEXICAL ONLY

### #1 — muslim 1776d · score: 17.99
> "This hadith has been narrated on the authority of Bara' with another chain of transmitters, but this hadith is short as compared with other ahadith which are more detailed."

**⚠ Misfire** — chain-of-transmission metadata. Keyword "compared" fires.

---

### #2 — bukhari 3334 · score: 16.26
> "Narrated Anas: The Prophet said, 'Allah will say to that person of the (Hell) Fire who will receive the least punishment, "If you had everything on the earth, would you give it as a ransom to free yourself (i.e. save yourself from this Fire)?" He will say, "Yes." Then Allah will say, "While you were in the backbone of Adam, I asked you much less than this, i.e. not to worship others besides Me, but you insisted on worshipping others besides me."'"

**⚠ Misfire** — "yourself" and "others" fire; topic is ransom on the Day of Judgment / shirk.

---

### #3 — muslim 2431 · score: 16.19
> "Abu Musa reported Allah's Messenger (may peace be upon him) as saying: There are many persons amongst men who are quite perfect but there are none perfect amongst women except Mary, daughter of 'Imran, Asiya wife of Pharaoh, and the excellence of 'A'isha as compared to women is that of Tharid over all other foods."

**⚠ Misfire** — "as compared to" fires; topic is the excellence of certain women.

---

### #4 — bukhari 4816 · score: 14.90
> "Narrated Ibn Mas'ud: (regarding) the Verse: 'And you have not been screening against yourself lest your ears, and your eyes and your skins should testify against you.' (41.22) While two persons from Quraish and their brother-in-law from Thaqif were in a house, they said to each other, 'Do you think that Allah hears our talks?' Some said, 'He hears a portion thereof.' Others said, 'If He can hear a portion of it, He can hear all of it.' Then the following Verse was revealed: 'And you have not been screening against yourself lest your ears, and your eyes and your skins should testify against you.' (41.22)"

**⚠ Misfire** — "yourself" keyword; topic is Allah's knowledge of all things.

---

### #5 — muslim 2939b · score: 14.88
> "Mughira b. Shu'ba reported that none asked Allah's Apostle (may peace be upon him) about Dajjal more than I asked him. I said: What did you ask? Mughira replied: I said that the people alleged that he would have a mountain load of bread and mutton and rivers of water. Thereupon he said: He would be more insignificant in the eye of Allah compared with all this."

**⚠ Misfire** — "compared" fires; topic is the Dajjal.

---

### #6 — abudawud 4627 · score: 14.88
> "Ibn 'Umar said: We used to say in the times of the Prophet (saws): We do not compare anyone with Abu Bakr. 'Umar came next and then 'Uthman. We then would leave (rest of) the companions of the Prophet (saws) without treating any as superior to other."

**⚠ Adjacent** — about ranking the Companions; not about self-comparison.

---

### #7 — bukhari 6557 · score: 14.38
> "Narrated Anas bin Malik: The Prophet said, 'Allah will say to the person who will have the minimum punishment in the Fire on the Day of Resurrection, "If you had things equal to whatever is on the earth, would you ransom yourself (from the punishment) with it?" He will reply, Yes. Allah will say, "I asked you a much easier thing than this while you were in the backbone of Adam, that is, not to worship others besides Me, but you refused and insisted to worship others besides Me."'"

**⚠ Misfire** — duplicate of #2 concept; "yourself" and "others" fire.

---

### #8 — bukhari 2219 · score: 14.33
> "Narrated Sa'd that his father said: 'Abdur-Rahman bin 'Auf said to Suhaib, 'Fear Allah and do not ascribe yourself to somebody other than your father.' Suhaib replied, 'I would not like to say it even if I were given large amounts of money, but I say I was kidnapped in my childhood.'"

**⚠ Misfire** — "ascribe yourself" fires; topic is lineage and identity.

---

### #9 — bukhari 3628 · score: 14.19
> "Narrated Ibn 'Abbas: Allah's Apostle in his fatal illness came out, wrapped with a sheet, and his head was wrapped with an oiled bandage. He sat on the pulpit, and praising and glorifying Allah, he said, 'Now then, people will increase but the Ansar will decrease in number, so much so that they, compared with the people, will be just like the salt in the meals. So, if any of you should take over the authority by which he can either benefit some people or harm some others, he should accept the goodness of their good people (i.e. Ansar) and excuse the faults of their wrong-doers.' That was the last gathering which the Prophet attended."

**⚠ Misfire** — "compared with the people" fires; topic is the Prophet's last address about the Ansar.

---

### #10 — bukhari 3655 · score: 14.04
> "Narrated Ibn 'Umar: We used to compare the people as to who was better during the lifetime of Allah's Apostle. We used to regard Abu Bakr as the best, then 'Umar, and then 'Uthman."

**⚠ Adjacent** — "compare the people" fires; topic is the ranking of the Companions.

---
---

## HYBRID — openai-small-en

### #1 — abudawud 4627 · score: 0.0285
> "Ibn 'Umar said: We used to say in the times of the Prophet (saws): We do not compare anyone with Abu Bakr. 'Umar came next and then 'Uthman. We then would leave (rest of) the companions of the Prophet (saws) without treating any as superior to other."

**⚠ Adjacent** — ranking Companions, not self-comparison.

---

### #2 — muslim 2963a · score: 0.0261
> "Abu Huraira reported that Allah's Messenger (may peace be upon him) said: When one of you looks at one who stands at a higher level than you in regard to wealth and physical structure he should also see one who stands at a lower level than you in regard to these things (in which he stands) at a higher level (as compared to him)."

**✅ On topic** — directly about comparing yourself to those above and below.

---

### #3 — bukhari 6407 · score: 0.0223
> "Narrated Abu Musa: The Prophet said, 'The example of the one who celebrates the Praises of his Lord (Allah) in comparison to the one who does not celebrate the Praises of his Lord, is that of a living creature compared to a dead one.'"

**⚠ Misfire** — "comparison" fires; topic is dhikr vs. no dhikr.

---

### #4 — muslim 1776d · score: 0.0164
> "This hadith has been narrated on the authority of Bara' with another chain of transmitters, but this hadith is short as compared with other ahadith which are more detailed."

**⚠ Misfire** — pulled in from lexical leg.

---

### #5 — adab 328 · score: 0.0164
> "Ibn 'Abbas said, 'When you want to mention your companion's faults, remember your own faults.'"

**✅ On topic** — self-reflection before judging others.

---

### #6 — bukhari 3334 · score: 0.0161
> "Narrated Anas: The Prophet said, 'Allah will say to that person of the (Hell) Fire who will receive the least punishment, "If you had everything on the earth, would you give it as a ransom to free yourself?" He will say, "Yes." Then Allah will say, "While you were in the backbone of Adam, I asked you much less than this, i.e. not to worship others besides Me, but you insisted on worshipping others besides me."'"

**⚠ Misfire** — pulled in from lexical leg; topic is the Day of Judgment.

---

### #7 — bukhari 6490 · score: 0.0161
> "Narrated Abu Huraira: Allah's Apostle said, 'If anyone of you looked at a person who was made superior to him in property and (in good) appearance, then he should also look at the one who is inferior to him.'"

**✅ On topic** — the core teaching on self-comparison.

---

### #8 — muslim 2431 · score: 0.0159
> "Abu Musa reported Allah's Messenger (may peace be upon him) as saying: There are many persons amongst men who are quite perfect but there are none perfect amongst women except Mary, daughter of 'Imran, Asiya wife of Pharaoh, and the excellence of 'A'isha as compared to women is that of Tharid over all other foods."

**⚠ Misfire** — pulled in from lexical leg.

---

### #9 — riyadussalihin 466 · score: 0.0159
> "Abu Hurairah (May Allah be pleased with him) reported: Messenger of Allah (PBUH) said, 'Look at those who are inferior to you and do not look at those who are superior to you, for this will keep you from belittling Allah's favour to you.' [Al-Bukhari and Muslim]. The narration in Al-Bukhari is: 'When one of you looks at someone who is superior to him in property and appearance, he should look at someone who is inferior to him.'"

**✅ On topic** — same teaching as #7, extended wording.

---

### #10 — bukhari 4816 · score: 0.0156
> "Narrated Ibn Mas'ud: (regarding) the Verse: 'And you have not been screening against yourself lest your ears, and your eyes and your skins should testify against you.' (41.22) While two persons from Quraish and their brother-in-law from Thaqif were in a house, they said to each other, 'Do you think that Allah hears our talks?' Some said, 'He hears a portion thereof.' Others said, 'If He can hear a portion of it, He can hear all of it.'"

**⚠ Misfire** — pulled in from lexical leg.

---

## HYBRID — openai-small-multi

### #1 — abudawud 4627 · score: 0.0283
> "Ibn 'Umar said: We used to say in the times of the Prophet (saws): We do not compare anyone with Abu Bakr. 'Umar came next and then 'Uthman. We then would leave (rest of) the companions of the Prophet (saws) without treating any as superior to other."

**⚠ Adjacent** — ranking Companions.

---

### #2 — muslim 2963a · score: 0.0261
> "Abu Huraira reported that Allah's Messenger (may peace be upon him) said: When one of you looks at one who stands at a higher level than you in regard to wealth and physical structure he should also see one who stands at a lower level than you in regard to these things (in which he stands) at a higher level (as compared to him)."

**✅ On topic**

---

### #3 — bukhari 6407 · score: 0.0223
> "Narrated Abu Musa: The Prophet said, 'The example of the one who celebrates the Praises of his Lord (Allah) in comparison to the one who does not celebrate the Praises of his Lord, is that of a living creature compared to a dead one.'"

**⚠ Misfire** — "comparison" keyword; topic is dhikr.

---

### #4 — tirmidhi 2323 · score: 0.0187
> "Qa'is bin Abi Hazim said: I heard Mustawrid, a member of Banu Fihr, saying: The Messenger of Allah (s.a.w) said: 'The world compared to the Hereafter is but like what one of you gets when placing his finger into the sea, so look at what you draw from it.'"

**⚠ Adjacent** — a comparison hadith, but the topic is the dunya vs. akhira, not self-comparison. Unique to this model (not in openai-small-en hybrid).

---

### #5 — muslim 1776d · score: 0.0164
> "This hadith has been narrated on the authority of Bara' with another chain of transmitters, but this hadith is short as compared with other ahadith which are more detailed."

**⚠ Misfire** — lexical leg noise.

---

### #6 — adab 328 · score: 0.0164
> "Ibn 'Abbas said, 'When you want to mention your companion's faults, remember your own faults.'"

**✅ On topic**

---

### #7 — bukhari 3334 · score: 0.0161
> "Narrated Anas: The Prophet said, 'Allah will say to that person of the (Hell) Fire who will receive the least punishment, "If you had everything on the earth, would you give it as a ransom to free yourself?" He will say, "Yes." Then Allah will say, "While you were in the backbone of Adam, I asked you much less than this, i.e. not to worship others besides Me, but you insisted on worshipping others besides me."'"

**⚠ Misfire** — lexical leg noise.

---

### #8 — bukhari 6490 · score: 0.0161
> "Narrated Abu Huraira: Allah's Apostle said, 'If anyone of you looked at a person who was made superior to him in property and (in good) appearance, then he should also look at the one who is inferior to him.'"

**✅ On topic**

---

### #9 — muslim 2431 · score: 0.0159
> "Abu Musa reported Allah's Messenger (may peace be upon him) as saying: There are many persons amongst men who are quite perfect but there are none perfect amongst women except Mary, daughter of 'Imran, Asiya wife of Pharaoh, and the excellence of 'A'isha as compared to women is that of Tharid over all other foods."

**⚠ Misfire** — lexical leg noise.

---

### #10 — riyadussalihin 466 · score: 0.0159
> "Abu Hurairah (May Allah be pleased with him) reported: Messenger of Allah (PBUH) said, 'Look at those who are inferior to you and do not look at those who are superior to you, for this will keep you from belittling Allah's favour to you.' [Al-Bukhari and Muslim]. The narration in Al-Bukhari is: 'When one of you looks at someone who is superior to him in property and appearance, he should look at someone who is inferior to him.'"

**✅ On topic**

---

## HYBRID — nomic

### #1 — abudawud 4627 · score: 0.0296
> "Ibn 'Umar said: We used to say in the times of the Prophet (saws): We do not compare anyone with Abu Bakr. 'Umar came next and then 'Uthman. We then would leave (rest of) the companions of the Prophet (saws) without treating any as superior to other."

**⚠ Adjacent** — ranking Companions.

---

### #2 — muslim 2963a · score: 0.0267
> "Abu Huraira reported that Allah's Messenger (may peace be upon him) said: When one of you looks at one who stands at a higher level than you in regard to wealth and physical structure he should also see one who stands at a lower level than you in regard to these things (in which he stands) at a higher level (as compared to him)."

**✅ On topic**

---

### #3 — bukhari 3655 · score: 0.0249
> "Narrated Ibn 'Umar: We used to compare the people as to who was better during the lifetime of Allah's Apostle. We used to regard Abu Bakr as the best, then 'Umar, and then 'Uthman."

**⚠ Adjacent** — ranking Companions; "compare" fires.

---

### #4 — mishkat 6025 · score: 0.0214
> "Ibn 'Umar said: In the time of the Prophet, we did not compare anyone with Abu Bakr. 'Umar came next and then Uthman. We would then leave the Prophet's companions without treating any as superior to others. Bukhari transmitted it. In a version by Abu Dawud, he said: When God's messenger was alive, we used to say that the most excellent member of the Prophet's people after himself was Abu Bakr, then 'Umar, then 'Uthman."

**⚠ Adjacent** — same concept as #1 and #3; Companions ranking.

---

### #5 — bukhari 3791 · score: 0.0206
> "Narrated Abu Humaid: The Prophet said, 'The best of the Ansar families (homes) are the families of Banu An-Najjar, and then that of Banu 'Abdul Ash-hal, and then that of Banu Al-Harith, and then that of Banu Saida; and there is good in all the families of the Ansar.' Sa'd bin 'Ubada followed us and said, 'O Abu Usaid! Don't you see that the Prophet compared the Ansar and made us the last of them in superiority?' Then Sa'd met the Prophet and said, 'O Allah's Apostle! In comparing the Ansar's families as to the degree of superiority, you have made us the last of them.' Allah's Apostle replied, 'Isn't it sufficient that you are regarded amongst the best?'"

**⚠ Misfire** — "compared" fires; topic is ranking of Ansar tribes.

---

### #6 — bukhari 6407 · score: 0.0194
> "Narrated Abu Musa: The Prophet said, 'The example of the one who celebrates the Praises of his Lord (Allah) in comparison to the one who does not celebrate the Praises of his Lord, is that of a living creature compared to a dead one.'"

**⚠ Misfire** — "comparison" fires; topic is dhikr.

---

### #7 — bukhari 3348 · score: 0.0167
> "Narrated Abu Sa'id Al-Khudri: The Prophet said, 'Allah will say, "O Adam." Adam will reply, "Labbaik wa Sa'daik." Allah will say, "Bring out the people of the fire." Adam will say, "O Allah! How many are the people of the Fire?" Allah will reply: "From every one thousand, take out nine-hundred-and-ninety-nine." At that time children will become hoary headed, every pregnant female will have a miscarriage, and one will see mankind as drunken, yet they will not be drunken, but dreadful will be the Wrath of Allah.' [...] The Prophet further said, 'By Him in Whose Hands my life is, hope that you will be one-fourth of the people of Paradise.' [...] 'You (Muslims) compared with non-Muslims are like a black hair in the skin of a white ox or like a white hair in the skin of a black ox (i.e. your number is very small as compared with theirs).'"

**⚠ Misfire** — "compared" fires; topic is the Day of Judgment and the proportion of Muslims in Paradise.

---

### #8 — muslim 1776d · score: 0.0164
> "This hadith has been narrated on the authority of Bara' with another chain of transmitters, but this hadith is short as compared with other ahadith which are more detailed."

**⚠ Misfire** — lexical leg noise.

---

### #9 — bukhari 6490 · score: 0.0164
> "Narrated Abu Huraira: Allah's Apostle said, 'If anyone of you looked at a person who was made superior to him in property and (in good) appearance, then he should also look at the one who is inferior to him.'"

**✅ On topic**

---

### #10 — bukhari 3334 · score: 0.0161
> "Narrated Anas: The Prophet said, 'Allah will say to that person of the (Hell) Fire who will receive the least punishment, "If you had everything on the earth, would you give it as a ransom to free yourself?" He will say, "Yes." Then Allah will say, "While you were in the backbone of Adam, I asked you much less than this, i.e. not to worship others besides Me, but you insisted on worshipping others besides me."'"

**⚠ Misfire** — lexical leg noise.

---

## HYBRID — mxbai

### #1 — muslim 2963a · score: 0.0270
> "Abu Huraira reported that Allah's Messenger (may peace be upon him) said: When one of you looks at one who stands at a higher level than you in regard to wealth and physical structure he should also see one who stands at a lower level than you in regard to these things (in which he stands) at a higher level (as compared to him)."

**✅ On topic**

---

### #2 — bukhari 3655 · score: 0.0259
> "Narrated Ibn 'Umar: We used to compare the people as to who was better during the lifetime of Allah's Apostle. We used to regard Abu Bakr as the best, then 'Umar, and then 'Uthman."

**⚠ Adjacent** — ranking Companions.

---

### #3 — abudawud 4627 · score: 0.0218
> "Ibn 'Umar said: We used to say in the times of the Prophet (saws): We do not compare anyone with Abu Bakr. 'Umar came next and then 'Uthman. We then would leave (rest of) the companions of the Prophet (saws) without treating any as superior to other."

**⚠ Adjacent** — ranking Companions; duplicate concept of #2.

---

### #4 — muslim 1776d · score: 0.0164
> "This hadith has been narrated on the authority of Bara' with another chain of transmitters, but this hadith is short as compared with other ahadith which are more detailed."

**⚠ Misfire** — lexical leg noise.

---

### #5 — forty 18 · score: 0.0164
> "The felicitous person takes lessons from (the actions of) others."

**✅ On topic**

---

### #6 — bukhari 3334 · score: 0.0161
> "Narrated Anas: The Prophet said, 'Allah will say to that person of the (Hell) Fire who will receive the least punishment, "If you had everything on the earth, would you give it as a ransom to free yourself?" He will say, "Yes." Then Allah will say, "While you were in the backbone of Adam, I asked you much less than this, i.e. not to worship others besides Me, but you insisted on worshipping others besides me."'"

**⚠ Misfire** — lexical leg noise.

---

### #7 — bukhari 6490 · score: 0.0161
> "Narrated Abu Huraira: Allah's Apostle said, 'If anyone of you looked at a person who was made superior to him in property and (in good) appearance, then he should also look at the one who is inferior to him.'"

**✅ On topic**

---

### #8 — muslim 2431 · score: 0.0159
> "Abu Musa reported Allah's Messenger (may peace be upon him) as saying: There are many persons amongst men who are quite perfect but there are none perfect amongst women except Mary, daughter of 'Imran, Asiya wife of Pharaoh, and the excellence of 'A'isha as compared to women is that of Tharid over all other foods."

**⚠ Misfire** — lexical leg noise.

---

### #9 — forty 3 · score: 0.0159
> "A Muslim is a mirror of the Muslim."

**✅ Adjacent** — metaphor about self-reflection through others.

---

### #10 — bukhari 4816 · score: 0.0156
> "Narrated Ibn Mas'ud: (regarding) the Verse: 'And you have not been screening against yourself lest your ears, and your eyes and your skins should testify against you.' (41.22) While two persons from Quraish and their brother-in-law from Thaqif were in a house, they said to each other, 'Do you think that Allah hears our talks?' Some said, 'He hears a portion thereof.' Others said, 'If He can hear a portion of it, He can hear all of it.' Then the following Verse was revealed: 'And you have not been screening against yourself lest your ears, and your eyes and your skins should testify against you.' (41.22)"

**⚠ Misfire** — lexical leg noise.

---
---

## SEMANTIC — openai-small-en

### #1 — adab 328 · score: 0.6896
> "Ibn 'Abbas said, 'When you want to mention your companion's faults, remember your own faults.'"

**✅ On topic** — self-reflection before judging others.

---

### #2 — bukhari 6490 · score: 0.6896
> "Narrated Abu Huraira: Allah's Apostle said, 'If anyone of you looked at a person who was made superior to him in property and (in good) appearance, then he should also look at the one who is inferior to him.'"

**✅ On topic** — the core teaching on comparison.

---

### #3 — riyadussalihin 466 · score: 0.6851
> "Abu Hurairah (May Allah be pleased with him) reported: Messenger of Allah (PBUH) said, 'Look at those who are inferior to you and do not look at those who are superior to you, for this will keep you from belittling Allah's favour to you.' [Al-Bukhari and Muslim]. The narration in Al-Bukhari is: 'When one of you looks at someone who is superior to him in property and appearance, he should look at someone who is inferior to him.'"

**✅ On topic** — same teaching with fuller wording.

---

### #4 — ahmad 111 · score: 0.6775
> "It was narrated from al-Harith bin Mu'awiyah al-Kindi, that he travelled to meet 'Umar bin al-Khattab and ask him about three things. [...] He said: I am afraid that if you tell them stories (for preaching), you will think that you are better than them, then you will tell them stories and think that you are better than them, until you imagine that you are as far above them as the Pleiades, then Allah will put you that far beneath their feet on the Day of Resurrection."

**✅ Adjacent** — the danger of feeling superior to others.

---

### #5 — forty 18 · score: 0.6753
> "The felicitous person takes lessons from (the actions of) others."

**✅ On topic**

---

### #6 — muslim 2963c · score: 0.6708
> "Abu Huraira reported Allah's Messenger (may peace be upon him) as saying: Look at those who stand at a lower level than you but don't look at those who stand at a higher level than you, for that is better-suited that you do not disparage Allah's favors."

**✅ On topic** — another narration of the core teaching; surfaces with size=100 (was absent from size=10 results).

---

### #7 — adab 592 · score: 0.6669
> "Abu Hurayra said, 'One of you looks at the mote in his brother's eye while forgetting the stump in his own eye.'"

**✅ On topic** — self-awareness before judging others; Biblical parallel (Matthew 7:3).

---

### #8 — muslim 2963a · score: 0.6666
> "Abu Huraira reported that Allah's Messenger (may peace be upon him) said: When one of you looks at one who stands at a higher level than you in regard to wealth and physical structure he should also see one who stands at a lower level than you in regard to these things (in which he stands) at a higher level (as compared to him)."

**✅ On topic** — core teaching on self-comparison; surfaces with size=100 (was absent from size=10 results).

---

### #9 — abudawud 4084 · score: 0.6659
> "Narrated AbuJurayy Jabir ibn Salim al-Hujaymi: [...] I said: Give me some advice. He said: Do not abuse anyone. [...] Do not look down upon any good work, and when you speak to your brother, show him a cheerful face. This is a good work. [...] And if a man abuses and shames you for something which he finds in you, then do not shame him for something which you find in him; he will bear the evil consequences for it."

**✅ Adjacent** — advice about treating others and not shaming them for faults you share.

---

### #10 — bulugh 1471 · score: 0.6640
> "Ibn 'Umar (RAA) narrated that the Messenger of Allah (P.B.U.H.) said, 'He who imitates any people (in their actions) is considered to be one of them.' Related by Abu Dawud and Ibn Hibban graded it as Sahih."

**⚠ Adjacent** — imitation/identification with others; loosely related.

---

## SEMANTIC — openai-small-multi

### #1 — adab 328 · score: 0.6898
> "Ibn 'Abbas said, 'When you want to mention your companion's faults, remember your own faults.'"

**✅ On topic**

---

### #2 — bukhari 6490 · score: 0.6894
> "Narrated Abu Huraira: Allah's Apostle said, 'If anyone of you looked at a person who was made superior to him in property and (in good) appearance, then he should also look at the one who is inferior to him.'"

**✅ On topic**

---

### #3 — riyadussalihin 466 · score: 0.6850
> "Abu Hurairah (May Allah be pleased with him) reported: Messenger of Allah (PBUH) said, 'Look at those who are inferior to you and do not look at those who are superior to you, for this will keep you from belittling Allah's favour to you.' [Al-Bukhari and Muslim]. The narration in Al-Bukhari is: 'When one of you looks at someone who is superior to him in property and appearance, he should look at someone who is inferior to him.'"

**✅ On topic**

---

### #4 — ahmad 111 · score: 0.6779
> "It was narrated from al-Harith bin Mu'awiyah al-Kindi, that he travelled to meet 'Umar bin al-Khattab and ask him about three things. [...] He said: I am afraid that if you tell them stories (for preaching), you will think that you are better than them, then you will tell them stories and think that you are better than them, until you imagine that you are as far above them as the Pleiades, then Allah will put you that far beneath their feet on the Day of Resurrection."

**✅ Adjacent** — the danger of feeling superior to others; surfaces with size=100 (was absent from size=10 results).

---

### #5 — forty 18 · score: 0.6752
> "The felicitous person takes lessons from (the actions of) others."

**✅ On topic** — surfaces with size=100 (was absent from size=10 results).

---

### #6 — muslim 2963c · score: 0.6709
> "Abu Huraira reported Allah's Messenger (may peace be upon him) as saying: Look at those who stand at a lower level than you but don't look at those who stand at a higher level than you, for that is better-suited that you do not disparage Allah's favors. In the chain narrated by Abu Mu'awiya's he said: Upon you."

**✅ On topic**

---

### #7 — adab 592 · score: 0.6667
> "Abu Hurayra said, 'One of you looks at the mote in his brother's eye while forgetting the stump in his own eye.'"

**✅ On topic**

---

### #8 — muslim 2963a · score: 0.6666
> "Abu Huraira reported that Allah's Messenger (may peace be upon him) said: When one of you looks at one who stands at a higher level than you in regard to wealth and physical structure he should also see one who stands at a lower level than you in regard to these things (in which he stands) at a higher level (as compared to him)."

**✅ On topic**

---

### #9 — abudawud 4084 · score: 0.6655
> "Narrated AbuJurayy Jabir ibn Salim al-Hujaymi: [...] Do not abuse anyone. [...] Do not look down upon any good work, and when you speak to your brother, show him a cheerful face. [...] And if a man abuses and shames you for something which he finds in you, then do not shame him for something which you find in him; he will bear the evil consequences for it."

**✅ Adjacent** — advice about treatment of others and not shaming.

---

### #10 — bulugh 1471 · score: 0.6634
> "Ibn 'Umar (RAA) narrated that the Messenger of Allah (P.B.U.H.) said, 'He who imitates any people (in their actions) is considered to be one of them.' Related by Abu Dawud and Ibn Hibban graded it as Sahih."

**⚠ Adjacent** — imitation of others; loosely related.

---

## SEMANTIC — nomic

### #1 — bukhari 6490 · score: 0.8354
> "Narrated Abu Huraira: Allah's Apostle said, 'If anyone of you looked at a person who was made superior to him in property and (in good) appearance, then he should also look at the one who is inferior to him.'"

**✅ On topic**

---

### #2 — bukhari 6061 · score: 0.8165
> "Narrated Abu Bakra: A man was mentioned before the Prophet and another man praised him greatly. The Prophet said, 'May Allah's Mercy be on you! You have cut the neck of your friend.' The Prophet repeated this sentence many times and said, 'If it is indispensable for anyone of you to praise someone, then he should say, "I think that he is so-and-so," if he really thinks that he is such. Allah is the One Who will take his accounts (as He knows his reality) and no-one can sanctify anybody before Allah.'"

**⚠ Adjacent** — about praising others excessively / judging others.

---

### #3 — bulugh 1471 · score: 0.8111
> "Ibn 'Umar (RAA) narrated that the Messenger of Allah (P.B.U.H.) said, 'He who imitates any people (in their actions) is considered to be one of them.' Related by Abu Dawud and Ibn Hibban graded it as Sahih."

**⚠ Adjacent** — imitation of others; loosely related.

---

### #4 — bukhari 6530 · score: 0.8109
> "Narrated Abu Sa'id: The Prophet said, 'Allah will say, "O Adam!" [...] "By Him in Whose Hand my soul is, I hope that you will be one half of the people of Paradise, as your (Muslims') example in comparison to the other people (non-Muslims), is like that of a white hair on the skin of a black ox, or a round hairless spot on the foreleg of a donkey."'"

**⚠ Misfire** — "in comparison" fires; topic is the Day of Judgment and proportions of Paradise.

---

### #5 — muslim 2963a · score: 0.8103
> "Abu Huraira reported that Allah's Messenger (may peace be upon him) said: When one of you looks at one who stands at a higher level than you in regard to wealth and physical structure he should also see one who stands at a lower level than you in regard to these things (in which he stands) at a higher level (as compared to him)."

**✅ On topic**

---

### #6 — tirmidhi 2513 · score: 0.8090
> "Abu Hurairah narrated that the Messenger of Allah (s.a.w) said: 'Look to one who is lower than you, and do not look to one who is above you. For indeed that is more worthy (so that you will) not belittle Allah's favors upon you.'"

**✅ On topic**

---

### #7 — bukhari 6162 · score: 0.8085
> "Narrated Abu Bakra: A man praised another man in front of the Prophet. The Prophet said thrice, 'Wailaka (Woe on you)! You have cut the neck of your brother!' The Prophet added, 'If it is indispensable for anyone of you to praise a person, then he should say, "I think that such-and-such person is so-and-so," and Allah is the one who will take his accounts (as he knows his reality) and none can sanctify anybody before Allah.'"

**⚠ Adjacent** — duplicate of #2 concept; about excessive praise.

---

### #8 — nasai 3947 · score: 0.8077
> "It was narrated from Abu Musa that the Prophet said: 'The superiority of 'Aishah to other women is like the superiority of Tharid to other kinds of food.'"

**⚠ Misfire** — "superiority to other" fires; topic is 'Aishah's excellence.

---

### #9 — abudawud 4627 · score: 0.8051
> "Ibn 'Umar said: We used to say in the times of the Prophet (saws): We do not compare anyone with Abu Bakr. 'Umar came next and then 'Uthman. We then would leave (rest of) the companions of the Prophet (saws) without treating any as superior to other."

**⚠ Adjacent** — ranking Companions, not self-comparison.

---

### #10 — adab 1146 · score: 0.8041
> "Ibn 'Abbas said, 'The most precious of people in my opinion is my sitting companion. This is so much the case that he can step over the shoulders of people until he sits with me.'"

**⚠ Misfire** — off topic; about valuing a companion.

---

## SEMANTIC — mxbai

### #1 — forty 18 · score: 0.8147
> "The felicitous person takes lessons from (the actions of) others."

**✅ On topic**

---

### #2 — bukhari 6490 · score: 0.8022
> "Narrated Abu Huraira: Allah's Apostle said, 'If anyone of you looked at a person who was made superior to him in property and (in good) appearance, then he should also look at the one who is inferior to him.'"

**✅ On topic**

---

### #3 — forty 3 · score: 0.7969
> "A Muslim is a mirror of the Muslim."

**✅ Adjacent** — metaphor about self-reflection through others.

---

### #4 — muslim 2963a · score: 0.7940
> "Abu Huraira reported that Allah's Messenger (may peace be upon him) said: When one of you looks at one who stands at a higher level than you in regard to wealth and physical structure he should also see one who stands at a lower level than you in regard to these things (in which he stands) at a higher level (as compared to him)."

**✅ On topic**

---

### #5 — ibnmajah 4336 · score: 0.7920
> "Sa'eed bin Al-Musayyab said that he met Abu Hurairah... [lengthy hadith about the marketplace of Paradise] '...Those who are of a lower status than them, and none of them will be regarded as insignificant, will sit on sandhills of musk and camphor, and they will not feel that those who are sitting on chairs are seated better than them.' [...] 'A man of elevated status will meet those who are of lower status than him, but none shall be regarded as insignificant... That is because no one should be sad there.'"

**[needs review]** — lengthy hadith about the marketplace of Paradise; includes passages on people of different status meeting without any feeling of inferiority.

---

### #6 — adab 159 · score: 0.7897
> "Abu'd-Darda' used to say to people: 'We know you better than the veterinarian knows his animals. We recognise the best of you from the worst of you. The best of you is the one whose good is hoped for and the one whose evil you are safe from. As for the worst of you, that is the person whose good is not hoped for and whose evil you are not safe from and he does not free slaves.'"

**[needs review]** — about discerning the best and worst among people.

---

### #7 — riyadussalihin 466 · score: 0.7864
> "Abu Hurairah (May Allah be pleased with him) reported: Messenger of Allah (PBUH) said, 'Look at those who are inferior to you and do not look at those who are superior to you, for this will keep you from belittling Allah's favour to you.' [Al-Bukhari and Muslim]. The narration in Al-Bukhari is: 'When one of you looks at someone who is superior to him in property and appearance, he should look at someone who is inferior to him.'"

**✅ On topic**

---

### #8 — muslim 2536 · score: 0.7854
> "'A'isha reported that a person asked Allah's Apostle (may peace be upon him) as to who amongst the people were the best. He said: Of the generation to which I belong, then of the second generation (generation adjacent to my generation), then of the third generation (generation adjacent to the second generation)."

**⚠ Adjacent** — ranking generations; "best" comparison but not about self.

---

### #9 — tirmidhi 2513 · score: 0.7821
> "Abu Hurairah narrated that the Messenger of Allah (s.a.w) said: 'Look to one who is lower than you, and do not look to one who is above you. For indeed that is more worthy (so that you will) not belittle Allah's favors upon you.'"

**✅ On topic**

---

### #10 — abudawud 4092 · score: 0.7821
> "Narrated AbuHurayrah: A man who was beautiful came to the Prophet (saws). He said: Messenger of Allah, I am a man who likes beauty, and I have been given some of it, as you see. And I do not like that anyone excels me (in respect of beauty). Is it pride? He replied: No, pride is disdaining what is true and despising people."

**[needs review]** — about a man concerned with being excelled by others in beauty; the Prophet defines pride as disdaining truth and despising people. This is the result that appeared in the UI but was absent from the original size=10 report.

---
---

## Summary

| Case | On-topic / 10 | Notes |
|---|---|---|
| Lexical (all models) | 0 / 10 | All keyword misfires — "yourself", "others", "compared" dominate |
| Hybrid – openai-small-en | 3 / 10 | #7 and #9 rescued by semantic leg; heavy lexical noise in #4, #6, #8, #10 |
| Hybrid – openai-small-multi | 3 / 10 | Nearly identical to en-only; tirmidhi 2323 unique at #4 (adjacent) |
| Hybrid – nomic | 2 / 10 | Companions-ranking cluster (#1, #3, #4, #5) dominates; lexical noise in #8, #10 |
| Hybrid – mxbai | 2 / 10 | Companions-ranking cluster again; lexical noise throughout |
| Semantic – openai-small-en | 4 or 5 / 10 [needs review] | size=100: #6/#8 are new on-topic results (muslim 2963c/2963a); tirmidhi 2513 and bukhari 7528 drop out |
| Semantic – openai-small-multi | 4 or 5 / 10 [needs recount] | size=100: ahmad 111 at #4, forty 18 at #5 (both new); tirmidhi 2513 and bukhari 7528 drop out |
| Semantic – nomic | 4 / 10 | size=100: abudawud 4627 enters at #9, nasai 3948 drops; #1–#8 unchanged |
| Semantic – mxbai | 6 / 10 | size=100: ibnmajah 4336 (#5) and adab 159 (#6) and abudawud 4092 (#10) are new; riyadussalihin 7 / forty 19 / forty 29 drop out |

> **Note on size=100:** Semantic sections were re-fetched with size=100 to match production PHP behavior. HNSW with larger size explores more candidates, surfacing higher-scoring docs that were missed at size=10. Rows marked [needs review] have either duplicate entries or results arguably not entirely on topic.

**openai-small-en vs openai-small-multi (semantic):** With size=100 the two models converge further — both now show ahmad 111, forty 18, muslim 2963c and 2963a in top-10. The models use the same underlying embedding (text-embedding-3-small) and the same inference endpoint, so divergence only comes from index coverage (English-only vs English+Arabic). Arabic-query testing would reveal more meaningful differences.

**Consistently correct hadiths across models (size=100):**
- **bukhari 6490** — appears in top-3 of every semantic case and in hybrid top-10 for all models. Ground-truth correct.
- **muslim 2963a** — appears in all 4 semantic cases (nomic #5, mxbai #4, en #8, multi #8) and all hybrid cases. Ground-truth correct.
- **riyadussalihin 466** — full-wording version of the same teaching; in openai en #3, openai multi #3, mxbai #7.
- **tirmidhi 2513** — now only in nomic (#6) and mxbai (#9); drops from openai semantic with size=100.
- **adab 328** — self-reflection angle; surfaces in both openai semantic cases at #1.
- **forty 18** — brief but on-topic; in mxbai #1, openai en #5, openai multi #5.

**Recurring issue:** muslim 1776d (a chain-of-transmission note with no substantive content) appears in hybrid results for all four models at a tied score of 0.0164, pulled in from the lexical leg. Worth filtering out hadiths with very short or content-free text at indexing time.
