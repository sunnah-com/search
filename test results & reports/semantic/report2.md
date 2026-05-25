# Exact kNN Search Report
**Query:** "comparing yourself to others"  
**Date:** 2026-05-20  
**Method:** Exact brute-force kNN — cosine similarity scored against every document's stored embedding  
**Results per case:** top 10

---

## Methodology

Standard semantic search in Elasticsearch uses HNSW (Hierarchical Navigable Small World), an approximate nearest-neighbor algorithm. HNSW explores only a subset of the index graph, so it can miss documents that are actually more similar to the query.

This report uses **exact brute-force kNN**: a Painless `script_score` query computes the full cosine similarity between the query embedding and every document's stored embedding, guaranteeing the true top-N results.

**Implementation:**
1. Query embedding obtained via the ES `_inference` API (same endpoint used during indexing).
2. `script_score` query with `match_all` reads each doc's `semantic_text.inference.chunks.embeddings` from `_source` and computes cosine similarity in Painless.
3. All docs in each index are scored — no graph traversal, no approximation.

**Scores:** Raw cosine similarity (range −1 to 1). To convert to the ES `semantic` query score format: `es_score = (cosine + 1) / 2`.

**Performance:** 6–12 seconds per model on 48k–141k documents (single-shard, single-node ES).

**Docs scored per model:**
| Model | Docs scored | Index total | Note |
|---|---|---|---|
| openai-small-en | 48,703 | ~99k | English docs with embeddings |
| openai-small-multi | 141,000 | ~285k | English + Arabic docs with embeddings |
| nomic | 48,703 | ~99k | English docs with embeddings |
| mxbai | 48,703 | ~99k | English docs with embeddings |

---

## Exact kNN — openai-small-en

### #1 — adab 328 · cosine: 0.3795 · equiv ES score: 0.6897
> "Ibn 'Abbas said, "When you want to mention your companion's faults, remember your own faults.""

---

### #2 — bukhari 6490 · cosine: 0.3789 · equiv ES score: 0.6895
> "Narrated Abu Huraira: Allah's Apostle said, "If anyone of you looked at a person who was made superior to him in property and (in good) appearance, then he should also look at the one who is inferior to him."

---

### #3 — riyadussalihin 466 · cosine: 0.3702 · equiv ES score: 0.6851
> "Abu Hurairah (May allah be pleased with him) reported: Messenger of Allah (PBUH) said, "Look at those who are inferior to you and do not look at those who are superior to you, for this will keep you from belittling Allah's favour to you." This is the wording in Sahih Muslim. [Al-Bukhari and Muslim] . The narration in Al-Bukhari is: Messenger of Allah (PBUH) said: "When one of you looks at someone who is superior to him in property and appearance, he should look at someone who is inferior to him"."

---

### #4 — ahmad 111 · cosine: 0.3543 · equiv ES score: 0.6772
> "It was narrated from al-Harith bin Mu'awiyah al-Kindi, that he travelled to meet ‘Umar bin al-Khattab and ask him about three things. He came to Madinah and ‘Umar asked him: What brought you here? He said: (I came) to ask you about three things. He said: What are they? He said: A woman and I may be in a confined space and the time for prayer comes, but if we both pray she will be standing next to me, and if she prays behind me she will have to go out of the space, ‘Umar said: Put a cloth to serve as a screen between you and her, and let her pray alongside you if you wish. (And I asked) about the two rak'ahs after 'Asr and he said: The Messenger of Allah ﷺ told me not to do them. He said: ..."

---

### #5 — forty 18 · cosine: 0.3507 · equiv ES score: 0.6754
> "The felicitous person takes lessons from (the actions of) others."

---

### #6 — muslim 2963 c · cosine: 0.3406 · equiv ES score: 0.6703
> "Abu Huraira reported Allah's Messenger (may peace be upon him) as saying: Look at those who stand at a lower level than you but don't look at those who stand at a higher level than you, for that is better-suited that you do not disparage Allah's favors. In the chain narrated by Abu Mu'awiya's he said: Upon you."

---

### #7 — adab 592 · cosine: 0.3337 · equiv ES score: 0.6668
> "Abu Hurayra said, "One of you looks at the mote in his brother's eye while forgetting the stump in his own eye.""

---

### #8 — muslim 2963 a · cosine: 0.3323 · equiv ES score: 0.6662
> "Abu Huraira reported that Allah's Messenger (may peace be upon him) said: When one of you looks at one who stands at a higher level than you in regard to wealth and physical structure he should also see one who stands at a lower level than you in regard to these things (in which he stands) at a higher level (as compared to him)."

---

### #9 — abudawud 4084 · cosine: 0.3312 · equiv ES score: 0.6656
> "Narrated AbuJurayy Jabir ibn Salim al-Hujaymi: I saw a man whose opinion was accepted by the people, and whatever he said they submitted to it. I asked: Who is he? They said: This is the Messenger of Allah (saws). I said: On you be peace, Messenger of Allah, twice. He said: Do not say "On you be peace," for "On you be peace" is a greeting for the dead, but say "Peace be upon you". I asked: You are the Messenger of Allah (may peace be upon you)? He said: I am the Messenger of Allah Whom you call when a calamity befalls you and He removes it; when you suffer from drought and you call Him, He grows food for you; and when you are in a desolate land or in a desert and your she-camel strays and..."

---

### #10 — bulugh 1471 · cosine: 0.3276 · equiv ES score: 0.6638
> "Ibn ’Umar (RAA) narrated that the Messenger of Allah (P.B.U.H.) said, “He who imitates any people (in their actions) is considered to be one of them.” Related by Abu Dawud and Ibn Hibban graded it as Sahih."

---


## Exact kNN — openai-small-multi

### #1 — adab 328 · cosine: 0.3795 · equiv ES score: 0.6897
> "Ibn 'Abbas said, "When you want to mention your companion's faults, remember your own faults.""

---

### #2 — bukhari 6490 · cosine: 0.3789 · equiv ES score: 0.6895
> "Narrated Abu Huraira: Allah's Apostle said, "If anyone of you looked at a person who was made superior to him in property and (in good) appearance, then he should also look at the one who is inferior to him."

---

### #3 — riyadussalihin 466 · cosine: 0.3702 · equiv ES score: 0.6851
> "Abu Hurairah (May allah be pleased with him) reported: Messenger of Allah (PBUH) said, "Look at those who are inferior to you and do not look at those who are superior to you, for this will keep you from belittling Allah's favour to you." This is the wording in Sahih Muslim. [Al-Bukhari and Muslim] . The narration in Al-Bukhari is: Messenger of Allah (PBUH) said: "When one of you looks at someone who is superior to him in property and appearance, he should look at someone who is inferior to him"."

---

### #4 — ahmad 111 · cosine: 0.3542 · equiv ES score: 0.6771
> "It was narrated from al-Harith bin Mu'awiyah al-Kindi, that he travelled to meet ‘Umar bin al-Khattab and ask him about three things. He came to Madinah and ‘Umar asked him: What brought you here? He said: (I came) to ask you about three things. He said: What are they? He said: A woman and I may be in a confined space and the time for prayer comes, but if we both pray she will be standing next to me, and if she prays behind me she will have to go out of the space, ‘Umar said: Put a cloth to serve as a screen between you and her, and let her pray alongside you if you wish. (And I asked) about the two rak'ahs after 'Asr and he said: The Messenger of Allah ﷺ told me not to do them. He said: ..."

---

### #5 — forty 18 · cosine: 0.3507 · equiv ES score: 0.6754
> "The felicitous person takes lessons from (the actions of) others."

---

### #6 — muslim 2963 c · cosine: 0.3406 · equiv ES score: 0.6703
> "Abu Huraira reported Allah's Messenger (may peace be upon him) as saying: Look at those who stand at a lower level than you but don't look at those who stand at a higher level than you, for that is better-suited that you do not disparage Allah's favors. In the chain narrated by Abu Mu'awiya's he said: Upon you."

---

### #7 — adab 592 · cosine: 0.3337 · equiv ES score: 0.6668
> "Abu Hurayra said, "One of you looks at the mote in his brother's eye while forgetting the stump in his own eye.""

---

### #8 — muslim 2963 a · cosine: 0.3323 · equiv ES score: 0.6662
> "Abu Huraira reported that Allah's Messenger (may peace be upon him) said: When one of you looks at one who stands at a higher level than you in regard to wealth and physical structure he should also see one who stands at a lower level than you in regard to these things (in which he stands) at a higher level (as compared to him)."

---

### #9 — abudawud 4084 · cosine: 0.3312 · equiv ES score: 0.6656
> "Narrated AbuJurayy Jabir ibn Salim al-Hujaymi: I saw a man whose opinion was accepted by the people, and whatever he said they submitted to it. I asked: Who is he? They said: This is the Messenger of Allah (saws). I said: On you be peace, Messenger of Allah, twice. He said: Do not say "On you be peace," for "On you be peace" is a greeting for the dead, but say "Peace be upon you". I asked: You are the Messenger of Allah (may peace be upon you)? He said: I am the Messenger of Allah Whom you call when a calamity befalls you and He removes it; when you suffer from drought and you call Him, He grows food for you; and when you are in a desolate land or in a desert and your she-camel strays and..."

---

### #10 — bulugh 1471 · cosine: 0.3276 · equiv ES score: 0.6638
> "Ibn ’Umar (RAA) narrated that the Messenger of Allah (P.B.U.H.) said, “He who imitates any people (in their actions) is considered to be one of them.” Related by Abu Dawud and Ibn Hibban graded it as Sahih."

---


## Exact kNN — nomic

### #1 — bukhari 6490 · cosine: 0.671 · equiv ES score: 0.8355
> "Narrated Abu Huraira: Allah's Apostle said, "If anyone of you looked at a person who was made superior to him in property and (in good) appearance, then he should also look at the one who is inferior to him."

---

### #2 — bukhari 6061 · cosine: 0.6323 · equiv ES score: 0.8161
> "Narrated Abu Bakra: A man was mentioned before the Prophet and another man praised him greatly The Prophet said, "May Allah's Mercy be on you ! You have cut the neck of your friend." The Prophet repeated this sentence many times and said, "If it is indispensable for anyone of you to praise someone, then he should say, 'I think that he is so-and-so," if he really thinks that he is such. Allah is the One Who will take his accounts (as He knows his reality) and no-one can sanctify anybody before Allah." (Khalid said, "Woe to you," instead of "Allah's Mercy be on you.")"

---

### #3 — bukhari 6530 · cosine: 0.6227 · equiv ES score: 0.8114
> "Narrated Abu Sa`id: The Prophet said, "Allah will say, 'O Adam!. Adam will reply, 'Labbaik and Sa`daik (I respond to Your Calls, I am obedient to Your orders), wal Khair fi Yadaik (and all the good is in Your Hands)!' Then Allah will say (to Adam), Bring out the people of the Fire.' Adam will say, 'What (how many) are the people of the Fire?' Allah will say, 'Out of every thousand (take out) nine hundred and ninety-nine (persons).' At that time children will become hoary-headed and every pregnant female will drop her load (have an abortion) and you will see the people as if they were drunk, yet not drunk; But Allah's punishment will be very severe." That news distressed the companions of ..."

---

### #4 — bulugh 1471 · cosine: 0.6218 · equiv ES score: 0.8109
> "Ibn ’Umar (RAA) narrated that the Messenger of Allah (P.B.U.H.) said, “He who imitates any people (in their actions) is considered to be one of them.” Related by Abu Dawud and Ibn Hibban graded it as Sahih."

---

### #5 — muslim 2963 a · cosine: 0.6211 · equiv ES score: 0.8105
> "Abu Huraira reported that Allah's Messenger (may peace be upon him) said: When one of you looks at one who stands at a higher level than you in regard to wealth and physical structure he should also see one who stands at a lower level than you in regard to these things (in which he stands) at a higher level (as compared to him)."

---

### #6 — tirmidhi 2513 · cosine: 0.6181 · equiv ES score: 0.8091
> "Abu Hurairah narrated that the Messenger of Allah (s.a.w) said: "Look to one who is lower than you, and do not look to one who is above you. For indeed that is more worthy(so that you will) not belittle Allah's favors upon you.""

---

### #7 — nasai 3947 · cosine: 0.6161 · equiv ES score: 0.808
> "It was narrated from Abu Musa that the Prophet said: "The superiority of 'Aishah to other women is like the superiority of Tharid to other kinds of food.""

---

### #8 — bukhari 6162 · cosine: 0.6136 · equiv ES score: 0.8068
> "Narrated Abu Bakra: A man praised another man in front of the Prophet. The Prophet said thrice, "Wailaka (Woe on you) ! You have cut the neck of your brother!" The Prophet added, "If it is indispensable for anyone of you to praise a person, then he should say, "I think that such-and-such person (is so-and-so), and Allah is the one who will take his accounts (as he knows his reality) and none can sanctify anybody before Allah (and that only if he knows well about that person.)"."

---

### #9 — abudawud 4627 · cosine: 0.6096 · equiv ES score: 0.8048
> "Ibn ‘Umar said: We used to say in the times of the Prophet (saws): We do not compare anyone with Abu Bakr. ’Umar came next and then ‘Uthman. We then would leave (rest of) the companions of the Prophet (saws) without treating any as superior to other."

---

### #10 — adab 1146 · cosine: 0.6093 · equiv ES score: 0.8046
> "Ibn 'Abbas said, "The most precious of people in my opinion is my sitting companion. This is so much the case that he can step over the shoulders of people until he sits with me.""

---


## Exact kNN — mxbai

### #1 — forty 18 · cosine: 0.6287 · equiv ES score: 0.8144
> "The felicitous person takes lessons from (the actions of) others."

---

### #2 — bukhari 6490 · cosine: 0.6062 · equiv ES score: 0.8031
> "Narrated Abu Huraira: Allah's Apostle said, "If anyone of you looked at a person who was made superior to him in property and (in good) appearance, then he should also look at the one who is inferior to him."

---

### #3 — forty 3 · cosine: 0.5944 · equiv ES score: 0.7972
> "A Muslim is a mirror of the Muslim."

---

### #4 — muslim 2963 a · cosine: 0.5875 · equiv ES score: 0.7937
> "Abu Huraira reported that Allah's Messenger (may peace be upon him) said: When one of you looks at one who stands at a higher level than you in regard to wealth and physical structure he should also see one who stands at a lower level than you in regard to these things (in which he stands) at a higher level (as compared to him)."

---

### #5 — ibnmajah 4336 · cosine: 0.5846 · equiv ES score: 0.7923
> "Sa’eed bin Al-Musayyab said that he met Abu Hurairah and Abu Hurairah said: “I supplicate Allah to bring you and I together in the marketplace of Paradise,” Sa’eed said: “Is there a marketplace there?” He said: “Yes. The Messenger of Allah (saw) told me that when the people of Paradise enter it, they will take their places according to their deeds, and they will be given permission for a length of time equivalent to Friday on earth, when they will visit Allah. His Throne will be shown to them and He will appear to them in one of the gardens of Paradise. Chairs of light and chairs of pearls and chairs of rubies and chairs of chrysolite and chairs of gold and chairs of silver will be placed..."

---

### #6 — adab 159 · cosine: 0.5824 · equiv ES score: 0.7912
> "Abu'd-Darda' used to say to people. "We know you better than the veterinarian knows his animals. We recognise the best of you from the worst of you. The best of you is the one whose good is hoped for and the one whose evil you are safe from. As for the worst of you, that is the person whose good is not hoped for and whose evil you are not safe from and he does not free slaves.""

---

### #7 — bukhari 3348 · cosine: 0.5786 · equiv ES score: 0.7893
> "Narrated Abu Sa`id Al-Khudri: The Prophet said, "Allah will say (on the Day of Resurrection), 'O Adam.' Adam will reply, 'Labbaik wa Sa`daik', and all the good is in Your Hand.' Allah will say: 'Bring out the people of the fire.' Adam will say: 'O Allah! How many are the people of the Fire?' Allah will reply: 'From every one thousand, take out nine-hundred-and ninety-nine.' At that time children will become hoary headed, every pregnant female will have a miscarriage, and one will see mankind as drunken, yet they will not be drunken, but dreadful will be the Wrath of Allah." The companions of the Prophet asked, "O Allah's Apostle! Who is that (excepted) one?" He said, "Rejoice with glad ti..."

---

### #8 — riyadussalihin 466 · cosine: 0.5742 · equiv ES score: 0.7871
> "Abu Hurairah (May allah be pleased with him) reported: Messenger of Allah (PBUH) said, "Look at those who are inferior to you and do not look at those who are superior to you, for this will keep you from belittling Allah's favour to you." This is the wording in Sahih Muslim. [Al-Bukhari and Muslim] . The narration in Al-Bukhari is: Messenger of Allah (PBUH) said: "When one of you looks at someone who is superior to him in property and appearance, he should look at someone who is inferior to him"."

---

### #9 — muslim 2536 · cosine: 0.5716 · equiv ES score: 0.7858
> "'A'isha reported that a person asked Allah's Apostle (may peace be upon him) as to who amongst the people were the best. He said: Of the generation to which I belong, then of the second generation (generation adjacent to my generation), then of the third generation (generation adjacent to the second generation)."

---

### #10 — nasai 384b · cosine: 0.5656 · equiv ES score: 0.7828
> "(Another chain) with similarity."

---


---

## Comparison: Exact kNN vs HNSW (size=100)

HNSW results are from report1.md semantic sections (re-fetched with size=100). ES semantic scores converted to cosine via `cosine = 2 × es_score − 1` for comparison.

### openai-small-en

**Identical.** Both methods return the same top 10 in the same order. HNSW with size=100 was sufficient for this model and query.

### openai-small-multi

**Identical.** Same top 10 as openai-small-en (same English docs, same embeddings from the same model). Divergence would appear for Arabic queries where the multilingual index has unique coverage.

### nomic

**Same docs, two pairs swapped.** All 10 docs appear in both, but HNSW got the ranking wrong for two adjacent-score pairs:

| Rank | HNSW (size=100) | Exact kNN |
|---|---|---|
| #3 | bulugh 1471 (cosine ≈ 0.6222) | **bukhari 6530 (cosine 0.6227)** |
| #4 | bukhari 6530 (cosine ≈ 0.6218) | **bulugh 1471 (cosine 0.6218)** |
| #7 | bukhari 6162 (cosine ≈ 0.617) | **nasai 3947 (cosine 0.6161)** |
| #8 | nasai 3947 (cosine ≈ 0.6154) | **bukhari 6162 (cosine 0.6136)** |

Score deltas are < 0.001 — HNSW graph traversal resolved ties incorrectly for both pairs.

### mxbai

**Two docs missed, two ghost docs.** Most significant discrepancy across all models:

| Rank | HNSW (size=100) | Exact kNN | Delta |
|---|---|---|---|
| #5 | ibnmajah 4336 ✓ | ibnmajah 4336 ✓ | same |
| #6 | adab 159 ✓ | adab 159 ✓ | same |
| #7 | riyadussalihin 466 (≈ 0.573) | **bukhari 3348 (0.5786)** | HNSW missed |
| #8 | muslim 2536 ✓ | muslim 2536 ✓ | shifted ranks |
| #9 | tirmidhi 2513 (≈ 0.564) | muslim 2536 | HNSW ghost |
| #10 | abudawud 4092 (≈ 0.564) | **nasai 384b (0.5656)** | HNSW ghost / missed |

**HNSW ghost docs**: tirmidhi 2513 and abudawud 4092 appear in the HNSW top 10 but their true cosine (≈ 0.564) is below nasai 384b (0.5656), so they fall outside the exact top 10.

**HNSW missed**: bukhari 3348 (cosine 0.5786) — its true similarity is higher than riyadussalihin 466 (≈ 0.573) which HNSW returned at that slot, yet HNSW never found it.

> **Note on nasai 384b:** Content-free chain-of-transmission metadata ("(Another chain) with similarity."). Appears at exact #10 as a model artifact. A minimum text-length filter at indexing time would exclude it.

---

## Summary

| Model | Exact vs HNSW (size=100) | Key finding |
|---|---|---|
| openai-small-en | ✓ Identical | HNSW fully accurate for this model/query |
| openai-small-multi | ✓ Identical | Same English docs, same embeddings |
| nomic | Same docs, 2 rank swaps | HNSW ranking errors < 0.001 cosine — negligible |
| mxbai | 2 docs missed, 2 ghost docs | HNSW missed bukhari 3348 (higher true cosine than docs it returned) |
