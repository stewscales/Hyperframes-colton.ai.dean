"""The eight shorts cut from the Trader to Coach long-form video.
Word numbers index assets/words.json (forced-aligned transcript of the full video, source time).
Each clip is a list of snippets (inclusive word ranges) played in the order given; pauses inside a snippet are
tightened by scripts/shorts.py. Per snippet:
  w      (first word, last word)
  z      framing the snippet opens on: 'W' wide, 'M' mid, 'T' tight (punch-in). Never upscaled (max 1.125x of 4K).
  steps  {word: framing} changes of framing inside the snippet (on the cut if the word follows one, otherwise a quick push-in)
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
   snips=[dict(w=(0, 25), z='M', steps={12: 'T'}),
          dict(w=(67, 97), z='W', steps={79: 'M', 88: 'T'}),
          dict(w=(184, 212), z='W', steps={197: 'T'}),
          dict(w=(1770, 1795), z='M', steps={1784: 'T'})],
   fix={1789: '"DOC"'}, hl={6, 24, 25, 190, 1789}, hero={24, 1789}, brk={2, 5, 7, 23, 72, 76, 187, 1774, 1776, 1779, 1788, 1790}, wide={92, 1790}),
 '02-the-bucket': dict(
   title='Picture a bucket',
   snips=[dict(w=(238, 270), z='M', steps={245: 'T', 258: 'W'}),
          dict(w=(749, 774), z='M', steps={760: 'T'}),
          dict(w=(1378, 1419), z='W', steps={1384: 'M', 1394: 'T', 1401: 'W', 1409: 'T'}),
          dict(w=(1729, 1745), z='M', steps={1739: 'T'}, end=15322)],
   fix={239: "let's", 240: '', 241: '', 259: '30'}, hl={244, 752, 1383, 1733}, hero={1383}, brk={250, 261, 264, 268, 756, 1381, 1731}, wide={756}),
 '03-conversations-yourself': dict(
   title='Have the conversations yourself',
   snips=[dict(w=(591, 677), z='M', start=5035,
               steps={604: 'T', 612: 'W', 626: 'M', 632: 'T', 638: 'M', 644: 'T', 652: 'W', 665: 'M', 676: 'T'})],
   tail=dict(cut=194.955, tone=195.08, hold=0.14),
   hl={603, 631, 677}, hero={603, 631}, brk={621, 630}),
 '04-hire-when-drowning': dict(
   title="We hire when we're drowning",
   snips=[dict(w=(1479, 1516), z='W', steps={1484: 'M', 1512: 'T'}),
          dict(w=(1552, 1559), z='W'),
          dict(w=(1611, 1635), z='M', steps={1628: 'T'}, end=14284)],
   fix={1506: 'on', 1627: 'People are'}, onset={1627: 473.67}, hl={1483, 1553, 1635}, hero={1483}, brk={1481, 1490, 1493, 1498, 1502, 1505, 1508, 1620, 1631}, wide={1493}),
 '05-first-content': dict(
   title="Your first content won't be good",
   snips=[dict(w=(495, 545), z='M', steps={501: 'W', 520: 'T', 528: 'M'}),
          dict(w=(426, 454), z='W', steps={442: 'M', 448: 'T'}),
          dict(w=(489, 494), z='W', steps={493: 'T'}, end=4158)],
   fix={519: ''}, hl={500, 527, 493, 494}, hero={500, 493}, brk={498, 512, 517, 533, 540, 432, 493}, wide={432, 540}),
 '06-too-wide': dict(
   title='"I coach traders" is too wide',
   snips=[dict(w=(299, 336), z='M', steps={305: 'T', 316: 'W', 318: 'M', 327: 'T'}),
          dict(w=(384, 404), z='W', steps={401: 'T'}, end=3407)],
   fix={299: '"I', 301: 'traders"', 318: '"I', 326: 'trading"', 334: '"oh', 336: 'me"', 399: 'you', 403: 'you'},
   hl={304, 311, 402}, hero={304}, brk={302, 312, 318, 334}),
 '07-ads-dont-create': dict(
   title="Ads and people don't create anything",
   snips=[dict(w=(98, 183), z='M', end=1457, steps={101: 'T', 115: 'W', 126: 'M', 144: 'T', 153: 'W', 170: 'M', 179: 'T'})],
   hl={105, 134, 183}, hero={183}, brk={104, 110, 148, 174, 183}, wide={110, 148, 174}),
 '08-one-thing-at-a-time': dict(
   title='One thing at a time',
   snips=[dict(w=(1640, 1686), z='M', start=14335, end=14754, steps={1647: 'T', 1660: 'W', 1674: 'T'})],
   fix={1666: '2-3', 1667: ''}, hl={1642, 1643, 1650}, hero={1642}, brk={1642, 1669, 1678, 1684}, wide={1674, 1678}),
}
