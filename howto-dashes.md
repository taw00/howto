<!--
https://blog.errantruminant.com/dashes/
https://github.com/taw00/howto/blob/master/howto-dashes.md
-->

Minuses, Hyphens and Dashes. Oh, My!
====================================

<!--Excerpt-->The dash family of punctuation—minus, hyphen, en dash, em dash, and more.

![dashes.png](appurtenances/dashes.png)

_Published November 1, 2019 — Updated November 2, 2019_

The Problem
-----------

If you write anything that is more substantive than a short social-media post or informal correspondence, em dashes are used quite frequently. En dashes are less common, but used occasionally. The problem: There is no key on the keyboard for the em, en dash, or minus sign. This can be maddening.

The first part of this article maps out the various dash-like punctuation characters, and why and how they are used when writing. The second part is a technical how-to for those wanting to make inserting such characters a bit more trouble free, particularly in the Linux GNOME Desktop Environment.



The Cheat Sheet (TL;DR)
-----------------------

<!--
- Minus (&minus;): `[CTRL][SHIFT][U]`, then `2 0 1 2 [ENTER]`
- Hyphen (-): typed directly from keyboard  
- En dash (–): `[compose]`, then `-` `-` `-`
- Em dash (—): `[compose]`, then `-` `-` `.`
-->

|   | html<br/>&code<br />&nbsp; | compose<br /><span style="font-size: 65%;">`[compose_key]`<br />&nbsp;</span> | unicode<br /><span style="font-size: 55%;">`[SHIFT][CTRL]U`<br />`[code][ENTER]`<br />&nbsp;</span> |
| - | :-: | :-: | :-: |
| minus&nbsp;&minus; | `&minus;` | &emsp; n/a &emsp; | `2`&nbsp;`2`&nbsp;`1`&nbsp;`2` |
| hyphen&nbsp;&hyphen;<br /><span style="font-size: 75%;">(- on the keyboard)</span> | `&hyphen;` | n/a | `2` `0` `1` `0` |
| en&nbsp;dash&nbsp;&ndash; | `&ndash;` | `-`&nbsp;`-`&nbsp;`.` | `2` `0` `1` `3` |
| em&nbsp;dash&nbsp;&mdash; | `&mdash;` | `-` `-` `-` | `2` `0` `1` `4` |
&nbsp;

| **specialized<br />rarely used**<br />&nbsp; | html<br/>&code<br />&nbsp; | compose<br /><span style="font-size: 65%;">`[compose_key]`<br />&nbsp;</span> | unicode<br /><span style="font-size: 55%;">`[SHIFT][CTRL]U`<br />`[code][ENTER]`</span> |
| - | :-: | :-: | :-: |
| hyphen,&nbsp;&#x2011;<br />non-breaking | `&#x2011;` | n/a | `2` `0` `1` `1` |
| figure&nbsp;dash&nbsp;&#x2012; | `&#x2012;`  | n/a | `2` `0` `1` `2` |
| quotation&nbsp;<br />dash&nbsp;&horbar;<br /><span style="font-size: 75%;">(aka horizontal bar)</span> | `&horbar;` | n/a | `2` `0` `1` `5` |



About Minuses, Hyphens, and Dashes
----------------------------------

Minuses equal the width of other arithmetic symbols and are vertically aligned. Em Dashes are approximately the width of the letter "M", En Dashes the width of the letter "N", and Hyphens shorter still. Figure Dashes, and Quotation Dashes are more rare and unique, but have their own specifications.

**Minuses** are used in arithmetic expressions:  
&emsp;_5&minus;4&plus;1&equals;2_  
&emsp;. . . if a hyphen is used instead, the difference can be subtle, but noticable:  
&emsp;_5&hyphen;4&plus;1&equals;2_

**Hyphens** are used to hyphenate a compound word and often non-inclusive numbers (example, telephone, social security, ISBN, etc.):  
  &emsp;_merry&hyphen;go&hyphen;round_  
  &emsp;978&hyphen;0&hyphen;226&hyphen;15906&hyphen;5&nbsp;(ISBN)

**En dashes** are not used as often, but are intended to be used for expressions of range (time, numbers, etc.), most often as a replacement for the word "to", and indicate that the values are inclusive:  
  &emsp;_Years 1900&ndash;2000._  
  &emsp;_The New York&ndash;San Francisco route._  
  &emsp;_The score was 27&ndash;17._

**Em dashes** are used for two primary purposes: 1. They are used to indicate a stronger break in a sentence than commas or parentheses. 2. They are used similarly to colons, but with a smidge more drama.

Em dashes in place of commas or parenthesis:  
  &emsp;_The anniversary of the eruption of Mount St. Helens&mdash;May 18, 1980&mdash;brought_  
  &emsp;_back vivid memories of ash and darkness._

Em dash in place of a colon:  
  &emsp;_There was only one thing missing from the pirate ship—pirates._

Em dashes are also used in citations, to indicate interruptions, to indicate blotted out text, and more. But that won't be discussed here.

Read more about when to use hyphens, dashes, colons, parentheses, etc. from this mini-bibliograpy. It also demonstrates how the special character, the 3-em dash (`&#x2E3B;` or `&#11835;`), is utilized in citations:

<div style="font-size: 75%; padding: 0 0 0 3em;">

Fogarty, Mignon (GrammarGirl). "Dashes, Colons, and Commas." Episode \#318. _Quick and Dirty Tips_, April 19, 2012, <https://www.quickanddirtytips.com/education/grammar/dashes-colons-and-commas>.

&#x2E3B;. "Dashes, Parentheses, and Commas: Sometimes they're interchangeable, sometimes they're not." Episode \#222. _Quick and Dirty Tips_, May 21, 2010, <https://www.quickanddirtytips.com/education/grammar/dashes-parentheses-and-commas>.

&#x2E3B;. "Hyphens: Is the glass half full or half-empty?" Episode \#093. _Quick and Dirty Tips_, February 1, 2008, <https://www.quickanddirtytips.com/education/grammar/hyphens>.

The Punctuation Guide. "En Dash." Accessed November 1, 2019, <https://www.thepunctuationguide.com/en-dash.html>.

&#x2E3B;. "Em Dash." Accessed November 1, 2019, <https://www.thepunctuationguide.com/em-dash.html>.

Emma. "Em Dash (—) vs En Dash (–): When to Use Dashes with Examples." _ESL: English as a Second Language for Teachers & Students_, April 12, 2019, <https://7esl.com/em-dash-en-dash/>.

</div>

**Figure Dashes** are essentially en dashes, but more specifically used in things like phone numbers:     
&emsp;_1&#x2012;800&#x2012;867&#x2012;5309_

**Quotation Dashes** are used for things like dialogue in certain styles of writing (Charles Frazier, James Joyce), though often em dashes are used instead:  
  &emsp;_&horbar;Oh, my! Dashes can be complicated, said the young journalist._  
  &emsp;. . . another example:  
  &emsp;_&horbar;I'm thinking on it, Inman said. How did you get in this fix?_

For more information about figure and quotation dashes (out of scope), read these: [Figure Dash](https://en.wikipedia.org/wiki/Dash#Figure_dash), [Quotation Dash](https://en.wikipedia.org/wiki/Quotation_mark#Quotation_dash). 2-em dashes and 3-em dashes are way outside the scope of this document. Refer to a [style guide](https://en.wikipedia.org/wiki/The_Chicago_Manual_of_Style) for guidance.

###### A Visual Comparison

  &emsp;minus **hyphen** en dash **em dash** figure dash **quotation dash**  
  &emsp;&minus; **&hyphen;** &ndash; **&mdash;** &#x2012; **&horbar;**  
  &emsp;&minus;minus&minus;  
  &emsp;&hyphen;hyphen&hyphen;  
  &emsp;&ndash;en dash&ndash;  
  &emsp;&mdash;em dash&mdash;  
  &emsp;&#x2012;figure dash&#x2012;  
  &emsp;&horbar;quotation dash&horbar;



> ----
>
> Note: For the remainder of this document, we are going to focus primarily on hyphens, en dashes, and em dashes. The discussion will also get a bit more technical in places. But if you are a writer in any capacity—especially if you are using Linux—you should know some of these techniques.
>
> ---



The Hyphen
----------

Inputting the hyphen on your keyboard is easy. The _hyphen key_ is just to right of the _0 key_ (zero-key) on most keyboards.

For most cases, the hyphen can be used in place of a minus sign, or even a figure dash. If you are displaying some light arithmetic equations though, you probably want to use the more precise character (the minus). Phone numbers generally use figure dashes. And if you want to ensure a word is not word-wrapped (like in a heading) the non-breaking hyphen is useful.

It should be noted that many people will just use hyphens in the place of en and em dashes as well (one or two hyphens for an en dash and two or three for an em dash), and many editors will overlook this, but if you are writing more formally, consider using the correct symbol instead. We no longer live in the days of typewriters.



Dashes in Word Processors
-------------------------

Inputting an em dash in a word processor _can be_ relatively easy. Most will replace any `[-][-][space]` with `—`. If a particular word processor does not enable this feature by default, look for the setting in the preferences menu somewhere and enable it if you like. I personally like to input these characters more directly from the keyboard. More on that in a second. For other characters, there is usually a "Insert special character" selection in one of the menus.



HTML- and Markdown-Formatted Documents
--------------------------------------

If you are creating an HTML- or Markdown-formatted document, a common method for inserting a special character is through the use of HTML ASCII or Unicode escape codes in the text. A few of these even have human-readable-ish entity names: `&minus;`, `&ndash;`, and `&mdash;`. And even `&horbar;`.

For example, this document was originally written in the Markdown format. It is very common to input these characters as HTML `&` escape codes, but I generally prefer to input the hyphen and em dashes directly from the keyboard. One great advantage of the escape codes, though, is that they eliminate ambiguity (the minus, hyphen, and en dash can look very similar).

More about Markdown can be found [here](https://en.wikipedia.org/wiki/Markdown), [here](https://commonmark.org/help/), and [here](https://www.markdownguide.org/extended-syntax). And more about HTML ASCII escape codes can be found [here](https://ascii.cl/htmlcodes.htm). You can use HTML escape codes in Markdown documents, not just HTML-formatted files.

Markdown is widely used in many MANY applications now. Most note-taking applications support it, some by default, or even nearly exclusively (example [Joplin](https://joplinapp.org), my personal favorite). But also forum software ([Discourse](https://www.discourse.org/)), blogging and website interfaces ([Ghost][919ee899] and [Wordpress][a7500213]), and many other applications.

  [919ee899]: https://ghost.org "Ghost Blogging Platform"
  [a7500213]: https://wordpress.org "Wordpress Web Publishing Platform"


----

The Various Methods of Inserting Special Characters
---------------------------------------------------

1. Googling it and then cut-n-pasting from Wikipedia or some such. Not recommended but it works in a pinch.
2. Using your application's "Insert Special Character" functionality (usually in some menu). Works okay for one-off needs, but (a) many applications don't have this capability, (b) the selection is limited, (c) it works differently for each application.
3. Typing `&` codes in a document that is HTML- or Markdown-formatted. Or in any text field that supports Markdown. It's a hack unless you are "coding" that document. When I am entering a comment in some forum, I want to insert these characters in a more natural way.
4. Unicode Input Method (using `[CRTL][SHIFT]U`, then `the code`). This is almost universal and is well worth learning, but the codes are hard to remember, even for the most basic characters. So, learn this, but the next method is more constructive for writers in an everyday setting.
5. Compose Key Method (using '[compose key]', then 'key combination'). This is the easiest and most natural method to "compose" the most common characters used for every day writing.

All of these methods will be discussed to some degree, but the two methods we will be focusing on are the Unicode Input Method and the Compose Key Method. The Compose Key Method needs to be enabled for every operating system a bit differently, here we will focus on the Linux GNOME Desktop Environment. There are links to instructions for other operating systems at the end of the article.

----

Enabling the Compose Key for Your Environment
---------------------------------------------

All of the various operating systems and their respective desktop environments give you a couple ways to enable special character input that allows uniform behavior no matter what application you are using. **For now,** for the purposes of this how-to, I am going to only describe how to enable the compose key in Linux's GNOME Desktop Environment, the default desktop environment for many favors of Linux, to include Fedora, RHEL, and Ubuntu.

> For other environments (Apple, Microsoft, or Linux running KDE or very old GNOME) take a look at the articles and links referenced after this next section.

### Enabling the Compose Key for the GNOME Desktop Environment

For these, a _Compose Key_ is used. In Fedora's GNOME environment it is not enabled by default. Or, at least, it was not in my desktop settings. To enable it, you need to install the "GNOME Tweak Tool", a package that gives you more power over configuration of the desktop.

**Installing the GNOME Tweak Tool**

Install from the desktop UI:
1. Open the "Software" application
2. Search for "GNOME Tweaks"
3. Install

Install from the command line:
- For Fedora and EL8, RHEL8/CentOS8):  
  `sudo dnf install gnome-tweaks -y`
- For Ubuntu (I _believe_ this is correct):  
  `sudo apt install gnome-tweak-tool`

**Enabling and Mapping the Compose Key**

1. Open "Tweaks"
2. Select "Keyboard & Mouse"
3. Look for "Compose Key" and click on "Disabled"
4. Flip the switch from "OFF" to "ON"
5. Choose what you use for your compose key. I use "Caps Lock"  
   <span style="font-size: 75%;">_Note: whatever you choose, this setting will
   override any other use for that key._</span>

### Enabling the Compose Key for Other Environments

Are you a Microsoft or Apple user? That's beyond the scope of this document (currently), but here's a good starting point: [5 Ways to Type a Dash](https://www.wikihow.com/Type-a-Dash).

Are you a Chromebook user? The Unicode Input Method works, but there is also a way to enable a Compose Key. Check out this extension: <https://chrome.google.com/webstore/detail/composekey/iijdllfdmhbmlmnbcohgbfagfibpbgba>. Good luck!

----

The Compose Key Method
----------------------

Now that you have enabled and mapped a designated Compose Key on your keyboard, open up a text editor (`gedit` on linux will work, but any will do) and let's give it a test drive. Heck, this will even work in any social-media message field if you'd like to try it there.

> <span style="font-size: 75%;">On my laptop, I mapped the `[compose]` key to my `[caps lock]` key. The `[hyphen]` listed here refers to the key to the right of the `[0]` key on the keyboard.</span>

For an en dash: `[compose]`, then `-` `-` `.`  
&emsp;i.e. `[compose]`, then `[hyphen]` `[hyphen]` `[period]`  
&emsp;_You should now see an en dash character (&ndash;)._

For an em dash: `[compose]`, then `-` `-` `-`  
&emsp;i.e. `[compose]`, then `[hyphen]` `[hyphen]` `[hyphen]`  
&emsp;_You should now see an em dash character (&mdash;)._

The Unicode Input Method
------------------------

You can use the Unicode input method instead of using the compose key. It's a bigger PITA and hard to remember, but useful to know if you ever need to insert other special characters not found on the keyboard. **And it works with most operating systems, to include Chromebooks**.

> <span style="font-size: 75%;">A <span style="text-decoration: underline">`u`</span> (underlined, lowercase U) chararacter should appear upon the first key combination. And the `[ENTER]` at the end may or may not be necessary, depending on the environment and application.</span>

&emsp;`[CTRL][SHIFT][U]`, then `[unicode]` `[ENTER]`  

For example:
- Minus sign: (&minus;): `[CTRL][SHIFT][U]`, then `2 2 1 2 [ENTER]`
- Hyphen (&hyphen;): use the keyboard's native `-` key.  
- En dash (&ndash;): `[CTRL][SHIFT][U]`, then `2 0 1 3 [ENTER]`
- Em dash (&mdash;): `[CTRL][SHIFT][U]`, then `2 0 1 4 [ENTER]`
- Figure dash (&#x2012;): `[CTRL][SHIFT][U]`, then `2 0 1 2 [ENTER]`
- Quotation dash (&horbar;): `[CTRL][SHIFT][U]`, then `2 0 1 5 [ENTER]`

A great summary of some of the most used `[CTRL][SHIFT][U]` Unicode input codes can be found in the "Diacritics and punctuation" section of this article: [Linux keyboard text symbols: Compose key shortcuts](https://fsymbols.com/keyboard/linux/compose/).

An exhaustively comprehensive Unicode reference can be found [here](https://unicode-table.com/).

----

Happy Writing!
--------------

That's it! You should not be able to rather easily insert minuses, dashes, and more into your documents like a pro. Good luck and enjoy your writing. Writing that aims to be more exacting in its selection of punctuation.
