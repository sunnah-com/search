# kNN Search Report — num_candidates=10000
**Query:** "comparing yourself to others"  
**Date:** 2026-05-20  
**Method:** `knn` query on HNSW index with `num_candidates=10000` (ES hard maximum)  
**Results per case:** top 10

---

## Methodology

ES's `knn` query runs on the HNSW approximate nearest-neighbor index. The `num_candidates` parameter controls how many graph nodes are explored before returning `k` results — higher values improve accuracy at the cost of latency.

ES 8.16 hard-caps `num_candidates` at **10,000**. This report uses that maximum for every model.

**How this differs from the two previous reports:**
| Method | How it works | Candidates explored | Query time |
|---|---|---|---|
| Semantic search (production) | HNSW, `num_candidates` implicit (~1k) | ~1,000 | ~50ms |
| This report | HNSW, `num_candidates=10000` | 10,000 (ES max) | 0.05–1.2s |
| Exact kNN (report2) | script_score brute-force | All docs (48k–141k) | 6–12s |

**Index coverage explored:**
| Model | Index docs | Candidates | Coverage |
|---|---|---|---|
| openai-small-en | ~99k | 10,000 | ~10% |
| openai-small-multi | ~285k | 10,000 | ~3.5% |
| nomic | ~99k | 10,000 | ~10% |
| mxbai | ~99k | 10,000 | ~10% |

---

## kNN (10k) — openai-small-en

### #1 — adab 328 · score: 0.6896
> "Ibn 'Abbas said, "When you want to mention your companion's faults, remember your own faults.""

---

### #2 — bukhari 6490 · score: 0.6896
> "Narrated Abu Huraira: Allah's Apostle said, "If anyone of you looked at a person who was made superior to him in property and (in good) appearance, then he should also look at the one who is inferior to him."

---

### #3 — riyadussalihin 466 · score: 0.6851
> "Abu Hurairah (May allah be pleased with him) reported: Messenger of Allah (PBUH) said, "Look at those who are inferior to you and do not look at those who are superior to you, for this will keep you from belittling Allah's favour to you." This is the wording in Sahih Muslim. [Al-Bukhari and Muslim] . The narration in Al-Bukhari is: Messenger of Allah (PBUH) said: "When one of you looks at someone who is superior to him in property and appearance, he should look at someone who is inferior to him"."

---

### #4 — ahmad 111 · score: 0.6775
> "It was narrated from al-Harith bin Mu'awiyah al-Kindi, that he travelled to meet ‘Umar bin al-Khattab and ask him about three things. He came to Madinah and ‘Umar asked him: What brought you here? He said: (I came) to ask you about three things. He said: What are they? He said: A woman and I may be in a confined space and the time for prayer comes, but if we both pray she will be standing next to me, and if she prays behind me she will have to go out of the space, ‘Umar said: Put a cloth to serve as a screen between you and her, and let her pray alongside you if you wish. (And I asked) about the two rak'ahs after 'Asr and he said: The Messenger of Allah ﷺ told me not to do them. He said: ..."

---

### #5 — forty 18 · score: 0.6753
> "The felicitous person takes lessons from (the actions of) others."

---

### #6 — muslim 2963 c · score: 0.6708
> "Abu Huraira reported Allah's Messenger (may peace be upon him) as saying: Look at those who stand at a lower level than you but don't look at those who stand at a higher level than you, for that is better-suited that you do not disparage Allah's favors. In the chain narrated by Abu Mu'awiya's he said: Upon you."

---

### #7 — adab 592 · score: 0.6669
> "Abu Hurayra said, "One of you looks at the mote in his brother's eye while forgetting the stump in his own eye.""

---

### #8 — muslim 2963 a · score: 0.6666
> "Abu Huraira reported that Allah's Messenger (may peace be upon him) said: When one of you looks at one who stands at a higher level than you in regard to wealth and physical structure he should also see one who stands at a lower level than you in regard to these things (in which he stands) at a higher level (as compared to him)."

---

### #9 — abudawud 4084 · score: 0.6659
> "Narrated AbuJurayy Jabir ibn Salim al-Hujaymi: I saw a man whose opinion was accepted by the people, and whatever he said they submitted to it. I asked: Who is he? They said: This is the Messenger of Allah (saws). I said: On you be peace, Messenger of Allah, twice. He said: Do not say "On you be peace," for "On you be peace" is a greeting for the dead, but say "Peace be upon you". I asked: You are the Messenger of Allah (may peace be upon you)? He said: I am the Messenger of Allah Whom you call when a calamity befalls you and He removes it; when you suffer from drought and you call Him, He grows food for you; and when you are in a desolate land or in a desert and your she-camel strays and..."

---

### #10 — bulugh 1471 · score: 0.664
> "Ibn ’Umar (RAA) narrated that the Messenger of Allah (P.B.U.H.) said, “He who imitates any people (in their actions) is considered to be one of them.” Related by Abu Dawud and Ibn Hibban graded it as Sahih."

---


## kNN (10k) — openai-small-multi

### #1 — adab 328 · score: 0.6898
> "Ibn 'Abbas said, "When you want to mention your companion's faults, remember your own faults.""

---

### #2 — bukhari 6490 · score: 0.6894
> "Narrated Abu Huraira: Allah's Apostle said, "If anyone of you looked at a person who was made superior to him in property and (in good) appearance, then he should also look at the one who is inferior to him."

---

### #3 — riyadussalihin 466 · score: 0.685
> "Abu Hurairah (May allah be pleased with him) reported: Messenger of Allah (PBUH) said, "Look at those who are inferior to you and do not look at those who are superior to you, for this will keep you from belittling Allah's favour to you." This is the wording in Sahih Muslim. [Al-Bukhari and Muslim] . The narration in Al-Bukhari is: Messenger of Allah (PBUH) said: "When one of you looks at someone who is superior to him in property and appearance, he should look at someone who is inferior to him"."

---

### #4 — ahmad 111 · score: 0.6779
> "It was narrated from al-Harith bin Mu'awiyah al-Kindi, that he travelled to meet ‘Umar bin al-Khattab and ask him about three things. He came to Madinah and ‘Umar asked him: What brought you here? He said: (I came) to ask you about three things. He said: What are they? He said: A woman and I may be in a confined space and the time for prayer comes, but if we both pray she will be standing next to me, and if she prays behind me she will have to go out of the space, ‘Umar said: Put a cloth to serve as a screen between you and her, and let her pray alongside you if you wish. (And I asked) about the two rak'ahs after 'Asr and he said: The Messenger of Allah ﷺ told me not to do them. He said: ..."

---

### #5 — forty 18 · score: 0.6752
> "The felicitous person takes lessons from (the actions of) others."

---

### #6 — muslim 2963 c · score: 0.6709
> "Abu Huraira reported Allah's Messenger (may peace be upon him) as saying: Look at those who stand at a lower level than you but don't look at those who stand at a higher level than you, for that is better-suited that you do not disparage Allah's favors. In the chain narrated by Abu Mu'awiya's he said: Upon you."

---

### #7 — adab 592 · score: 0.6667
> "Abu Hurayra said, "One of you looks at the mote in his brother's eye while forgetting the stump in his own eye.""

---

### #8 — muslim 2963 a · score: 0.6666
> "Abu Huraira reported that Allah's Messenger (may peace be upon him) said: When one of you looks at one who stands at a higher level than you in regard to wealth and physical structure he should also see one who stands at a lower level than you in regard to these things (in which he stands) at a higher level (as compared to him)."

---

### #9 — abudawud 4084 · score: 0.6655
> "Narrated AbuJurayy Jabir ibn Salim al-Hujaymi: I saw a man whose opinion was accepted by the people, and whatever he said they submitted to it. I asked: Who is he? They said: This is the Messenger of Allah (saws). I said: On you be peace, Messenger of Allah, twice. He said: Do not say "On you be peace," for "On you be peace" is a greeting for the dead, but say "Peace be upon you". I asked: You are the Messenger of Allah (may peace be upon you)? He said: I am the Messenger of Allah Whom you call when a calamity befalls you and He removes it; when you suffer from drought and you call Him, He grows food for you; and when you are in a desolate land or in a desert and your she-camel strays and..."

---

### #10 — bulugh 1471 · score: 0.6634
> "Ibn ’Umar (RAA) narrated that the Messenger of Allah (P.B.U.H.) said, “He who imitates any people (in their actions) is considered to be one of them.” Related by Abu Dawud and Ibn Hibban graded it as Sahih."

---


## kNN (10k) — nomic

### #1 — bukhari 6490 · score: 0.8354
> "Narrated Abu Huraira: Allah's Apostle said, "If anyone of you looked at a person who was made superior to him in property and (in good) appearance, then he should also look at the one who is inferior to him."

---

### #2 — bukhari 6061 · score: 0.8165
> "Narrated Abu Bakra: A man was mentioned before the Prophet and another man praised him greatly The Prophet said, "May Allah's Mercy be on you ! You have cut the neck of your friend." The Prophet repeated this sentence many times and said, "If it is indispensable for anyone of you to praise someone, then he should say, 'I think that he is so-and-so," if he really thinks that he is such. Allah is the One Who will take his accounts (as He knows his reality) and no-one can sanctify anybody before Allah." (Khalid said, "Woe to you," instead of "Allah's Mercy be on you.")"

---

### #3 — bulugh 1471 · score: 0.8111
> "Ibn ’Umar (RAA) narrated that the Messenger of Allah (P.B.U.H.) said, “He who imitates any people (in their actions) is considered to be one of them.” Related by Abu Dawud and Ibn Hibban graded it as Sahih."

---

### #4 — bukhari 6530 · score: 0.8109
> "Narrated Abu Sa`id: The Prophet said, "Allah will say, 'O Adam!. Adam will reply, 'Labbaik and Sa`daik (I respond to Your Calls, I am obedient to Your orders), wal Khair fi Yadaik (and all the good is in Your Hands)!' Then Allah will say (to Adam), Bring out the people of the Fire.' Adam will say, 'What (how many) are the people of the Fire?' Allah will say, 'Out of every thousand (take out) nine hundred and ninety-nine (persons).' At that time children will become hoary-headed and every pregnant female will drop her load (have an abortion) and you will see the people as if they were drunk, yet not drunk; But Allah's punishment will be very severe." That news distressed the companions of ..."

---

### #5 — muslim 2963 a · score: 0.8103
> "Abu Huraira reported that Allah's Messenger (may peace be upon him) said: When one of you looks at one who stands at a higher level than you in regard to wealth and physical structure he should also see one who stands at a lower level than you in regard to these things (in which he stands) at a higher level (as compared to him)."

---

### #6 — tirmidhi 2513 · score: 0.809
> "Abu Hurairah narrated that the Messenger of Allah (s.a.w) said: "Look to one who is lower than you, and do not look to one who is above you. For indeed that is more worthy(so that you will) not belittle Allah's favors upon you.""

---

### #7 — bukhari 6162 · score: 0.8085
> "Narrated Abu Bakra: A man praised another man in front of the Prophet. The Prophet said thrice, "Wailaka (Woe on you) ! You have cut the neck of your brother!" The Prophet added, "If it is indispensable for anyone of you to praise a person, then he should say, "I think that such-and-such person (is so-and-so), and Allah is the one who will take his accounts (as he knows his reality) and none can sanctify anybody before Allah (and that only if he knows well about that person.)"."

---

### #8 — nasai 3947 · score: 0.8077
> "It was narrated from Abu Musa that the Prophet said: "The superiority of 'Aishah to other women is like the superiority of Tharid to other kinds of food.""

---

### #9 — abudawud 4627 · score: 0.8051
> "Ibn ‘Umar said: We used to say in the times of the Prophet (saws): We do not compare anyone with Abu Bakr. ’Umar came next and then ‘Uthman. We then would leave (rest of) the companions of the Prophet (saws) without treating any as superior to other."

---

### #10 — adab 1146 · score: 0.8041
> "Ibn 'Abbas said, "The most precious of people in my opinion is my sitting companion. This is so much the case that he can step over the shoulders of people until he sits with me.""

---


## kNN (10k) — mxbai

### #1 — forty 18 · score: 0.8147
> "The felicitous person takes lessons from (the actions of) others."

---

### #2 — bukhari 6490 · score: 0.8022
> "Narrated Abu Huraira: Allah's Apostle said, "If anyone of you looked at a person who was made superior to him in property and (in good) appearance, then he should also look at the one who is inferior to him."

---

### #3 — forty 3 · score: 0.7969
> "A Muslim is a mirror of the Muslim."

---

### #4 — muslim 2963 a · score: 0.794
> "Abu Huraira reported that Allah's Messenger (may peace be upon him) said: When one of you looks at one who stands at a higher level than you in regard to wealth and physical structure he should also see one who stands at a lower level than you in regard to these things (in which he stands) at a higher level (as compared to him)."

---

### #5 — ibnmajah 4336 · score: 0.792
> "Sa’eed bin Al-Musayyab said that he met Abu Hurairah and Abu Hurairah said: “I supplicate Allah to bring you and I together in the marketplace of Paradise,” Sa’eed said: “Is there a marketplace there?” He said: “Yes. The Messenger of Allah (saw) told me that when the people of Paradise enter it, they will take their places according to their deeds, and they will be given permission for a length of time equivalent to Friday on earth, when they will visit Allah. His Throne will be shown to them and He will appear to them in one of the gardens of Paradise. Chairs of light and chairs of pearls and chairs of rubies and chairs of chrysolite and chairs of gold and chairs of silver will be placed..."

---

### #6 — adab 159 · score: 0.7897
> "Abu'd-Darda' used to say to people. "We know you better than the veterinarian knows his animals. We recognise the best of you from the worst of you. The best of you is the one whose good is hoped for and the one whose evil you are safe from. As for the worst of you, that is the person whose good is not hoped for and whose evil you are not safe from and he does not free slaves.""

---

### #7 — bukhari 3348 · score: 0.7888
> "Narrated Abu Sa`id Al-Khudri: The Prophet said, "Allah will say (on the Day of Resurrection), 'O Adam.' Adam will reply, 'Labbaik wa Sa`daik', and all the good is in Your Hand.' Allah will say: 'Bring out the people of the fire.' Adam will say: 'O Allah! How many are the people of the Fire?' Allah will reply: 'From every one thousand, take out nine-hundred-and ninety-nine.' At that time children will become hoary headed, every pregnant female will have a miscarriage, and one will see mankind as drunken, yet they will not be drunken, but dreadful will be the Wrath of Allah." The companions of the Prophet asked, "O Allah's Apostle! Who is that (excepted) one?" He said, "Rejoice with glad ti..."

---

### #8 — riyadussalihin 466 · score: 0.7864
> "Abu Hurairah (May allah be pleased with him) reported: Messenger of Allah (PBUH) said, "Look at those who are inferior to you and do not look at those who are superior to you, for this will keep you from belittling Allah's favour to you." This is the wording in Sahih Muslim. [Al-Bukhari and Muslim] . The narration in Al-Bukhari is: Messenger of Allah (PBUH) said: "When one of you looks at someone who is superior to him in property and appearance, he should look at someone who is inferior to him"."

---

### #9 — muslim 2536 · score: 0.7854
> "'A'isha reported that a person asked Allah's Apostle (may peace be upon him) as to who amongst the people were the best. He said: Of the generation to which I belong, then of the second generation (generation adjacent to my generation), then of the third generation (generation adjacent to the second generation)."

---

### #10 — nasai 384b · score: 0.7824
> "(Another chain) with similarity."

---


---

## Comparison across all three methods

### openai-small-en

**All three methods identical.** HNSW (production size=100), kNN 10k, and exact brute-force return the same top 10 in the same order. The HNSW index is accurate for this model and query.

### openai-small-multi

**All three methods identical.** Same English docs, same embeddings from the same model. Multilingual divergence would appear for Arabic queries.

### nomic

**kNN 10k = HNSW size=100. Both differ from exact kNN at ranks #3/#4 and #7/#8.**

The same two ranking swaps persist at num_candidates=10000 as at the production default (~1k candidates). This means the HNSW graph topology itself has encoded the wrong neighbors for these near-identical-score pairs — increasing candidate count doesn't help because the graph is navigated to the same local optimum. Only brute-force resolves it.

| Rank | HNSW / kNN 10k | Exact kNN | Score delta |
|---|---|---|---|
| #3 | bulugh 1471 | **bukhari 6530** | < 0.001 cosine |
| #4 | bukhari 6530 | **bulugh 1471** | < 0.001 cosine |
| #7 | bukhari 6162 | **nasai 3947** | < 0.001 cosine |
| #8 | nasai 3947 | **bukhari 6162** | < 0.001 cosine |

The deltas are below 0.001 cosine, so the practical impact is minimal for search quality evaluation.

### mxbai

**kNN 10k = exact kNN. Both differ from HNSW size=100.**

At num_candidates=10000 (~10% of the index), the HNSW correctly identifies the true top-10 — the same results as exhaustive brute-force. The production setting (size=100, ~1k candidates) had approximation errors.

| Rank | HNSW size=100 (production) | kNN 10k / Exact |
|---|---|---|
| #7 | riyadussalihin 466 | **bukhari 3348** (score 0.7888) |
| #9 | tirmidhi 2513 | **muslim 2536** |
| #10 | abudawud 4092 | **nasai 384b** (score 0.7824) |

> **In short:** for mxbai, `num_candidates=10000` is sufficient to get exact-quality results. The production search (size=100 → ~1k candidates) misses bukhari 3348 and returns two ghost docs (tirmidhi 2513, abudawud 4092) that fall below the true top-10 cutoff.

---

## Summary

| Model | kNN 10k vs production (HNSW size=100) | kNN 10k vs exact brute-force |
|---|---|---|
| openai-small-en | ✓ Identical | ✓ Identical |
| openai-small-multi | ✓ Identical | ✓ Identical |
| nomic | ✓ Identical | ✗ 2 rank swaps (< 0.001 cosine) |
| mxbai | ✗ Different (fixes 2 ghost docs, finds bukhari 3348) | ✓ Identical |

**Takeaway:** `num_candidates=10000` adds 0.05–1.2s of latency but corrects mxbai's approximation errors without needing brute-force. For nomic's minor ranking swaps (< 0.001 cosine), neither candidate count helps — they're structural graph errors that only brute-force resolves.
