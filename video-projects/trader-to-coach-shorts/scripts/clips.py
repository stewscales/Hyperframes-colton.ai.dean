"""The eight shorts cut from the Trader to Coach long-form video (full original 4K landscape frame, no reframing or zoom).
Word numbers index assets/words.json (forced-aligned transcript of the full video, source time).
Each clip is a list of snippets (inclusive word ranges) played in the order given; pauses inside a snippet are
tightened by scripts/shorts.py. Per snippet:
  w      (first word, last word)
  start  optional first source frame (when the word before runs straight into the first word)
  end    optional end source frame (exclusive) - used to end a clip before he blinks / looks away / starts the next line
Captions are word-for-word what is said. Per clip:
  fix    {word: caption text}   corrections of the transcript / tidy numerals ('' drops the word from the caption)
  hl     words shown in brand blue (key words only)
  hero   words whose caption is shown in the large hero size
  brk / join   force / forbid a caption break before a word;  wide = phrases (by any word) kept as one two-line caption
  onset  {word: source time} where the aligner put a word start in the wrong place
  tail   the last word runs straight into the next sentence: voice ends at `cut` (source s), room tone from `tone` covers `hold` s
"""
CLIPS = {
 '01-wrong-order': dict(
   title='Most traders who try coaching quit in 90 days',
   snips=[dict(w=(0, 25)),
          dict(w=(67, 97)),
          dict(w=(184, 212)),
          dict(w=(1770, 1795))],
   fix={1789: '"DOC"'}, hl={6, 24, 25, 190, 1789}, hero={24, 1789}, brk={2, 5, 7, 23, 72, 76, 187, 1774, 1776, 1779, 1788, 1790}, wide={92, 1790}),
 '02-the-bucket': dict(
   title='Picture a bucket',
   snips=[dict(w=(238, 270), start=1881),              # frame 0 = the last eyes-open frame before he blinks through "First" (1882-1890); 1882+ opens on closed eyes
          dict(w=(749, 774)),
          dict(w=(1378, 1419)),
          dict(w=(1729, 1745), end=15320)],           # last frame 15319: "order" is out, eyes still on the lens (he looks down from 15320)
   tight=dict(min_pause=0.20, keep_after=0.09, keep_before=0.07, min_cut=3),   # polish pass: pauses of 0.2 s+ come down to about 0.16 s (the lead-in to each word is left alone)
   hold=26,                                            # the end frame is held just under a second so the last graphic can register
   fix={239: "let's", 240: '', 241: '', 259: '30'}, hl={244, 752, 1383, 1733}, hero={1383}, brk={250, 261, 264, 268, 756, 1381, 1731}, wide={756}),
 '03-conversations-yourself': dict(
   title='Have the conversations yourself',
   snips=[dict(w=(591, 677), start=5035)],
   tail=dict(cut=194.955, tone=195.08, hold=0.14),
   hl={603, 631, 677}, hero={603, 631}, brk={621, 630}),
 '04-hire-when-drowning': dict(
   title="We hire when we're drowning",
   snips=[dict(w=(1479, 1516)),
          dict(w=(1552, 1559)),
          dict(w=(1611, 1635), end=14284)],
   fix={1506: 'on', 1627: 'People are'}, onset={1627: 473.67}, hl={1483, 1553, 1635}, hero={1483}, brk={1481, 1490, 1493, 1498, 1502, 1505, 1508, 1620, 1631}, wide={1493}),
 '05-first-content': dict(
   title="Your first content won't be good",
   snips=[dict(w=(495, 545)),
          dict(w=(426, 454)),
          dict(w=(489, 494), end=4158)],
   fix={519: ''}, hl={500, 527, 493, 494}, hero={500, 493}, brk={498, 512, 517, 533, 540, 432, 493}, wide={432, 540}),
 '06-too-wide': dict(
   title='"I coach traders" is too wide',
   snips=[dict(w=(299, 336)),
          dict(w=(384, 404), end=3407)],
   fix={299: '"I', 301: 'traders"', 318: '"I', 326: 'trading"', 334: '"oh', 336: 'me"', 399: 'you', 403: 'you'},
   hl={304, 311, 402}, hero={304}, brk={302, 312, 318, 334}),
 '07-ads-dont-create': dict(
   title="Ads and people don't create anything",
   snips=[dict(w=(98, 183), end=1457)],
   hl={105, 134, 183}, hero={183}, brk={104, 110, 148, 174, 183}, wide={110, 148, 174}),
 '08-one-thing-at-a-time': dict(
   title='One thing at a time',
   snips=[dict(w=(0, 25), end=225),                       # hook from 01: "Most traders who try coaching will quit in the first 90 days..."
          dict(w=(1640, 1686), start=14335, end=14754)],
   fix={1666: '2-3', 1667: ''}, hl={1642, 1643, 1650}, hero={1642}, brk={1642, 1669, 1678, 1684}, wide={1674, 1678}),
}
