Minuses, Hyphens and Dashes Dashes. Oh, my!
===========================================

_or, How-To Input Dash-like Punctuation in the GNOME Desktop Environment_

TL;DR (the cheat sheet)
-----------------------

- Minus (&minus;): `[CTRL][SHIFT][U]`, then `2012[ENTER]`
- Hyphen (-): typed directly from keyboard  
- En dash (–): `[compose]`, then `[hyphen][hyphen][hyphen]`  
<span style="font-size: 75%;">_(i.e., `[compose]`, then `---`)_</span>  
- Em dash (—): `[compose]`, then `[hyphen][hyphen][period]`  
<span style="font-size: 75%;">_(i.e., `[compose]`, then `--.`)_</span>

|         | html<br/>&code  | compose | unicode |
| ------- | --------------- | ------- | --------|
| minus   | `&minus;`       | n/a     | 2212    |
| hyphen<br /><span style="font-size: 75%;">(use keyboard `-`)</span> | `&hyphen;` | n/a<br /><span style="font-size: 75%;">(keyboard `-`)</span> | 2010<br /><span style="font-size: 75%;">(keyboard `-`)</span> |
| en dash | `&ndash;`       | `--.`   | 2013    |
| em dash | `&mdash;`       | `---`   | 2014    |
|   |   |   |   |
| hyphen,<br />non-breaking | `&#x2011;` | ­n/a | 2011 |
| figure dash | `&#x2012;`  | n/a     | 2012    |
| quotation dash<br /><span style="font-size: 75%;">(aka horizontal bar)</span> | `&horbar;` | n/a     | 2015    |

About Minuses, Hyphens, and Dashes
----------------------------------

Em Dashes are approximately the width of the letter "M", En Dashes the width of
the letter "N", and Hyphens shorter still. Minuses equal the width of other
arithmetic symbols and are vertically aligned. Figure Dashes, and Quotation
Dashes are more rare and unique, but have their own specifications.

**Minuses** are used in arithmetic expressions:  
&emsp;_5&minus;4&plus;1&equals;2_  
&emsp;. . . if a hyphen from the keyboard were used instead:  
&emsp;_5-4&plus;1&equals;2_

**Hyphens** are used to hyphenate a compound word: _merry-go-round_.

**Figure Dashes** are used in things like phone numbers:
_1&#x2012;800&#x2012;867&#x2012;5309_

**Quotation Dashes** are used for things like dialogue in certain
styles of writing, though often em dashes are used instead:  
  &emsp;_&horbar;Oh, my! Dashes can be complicated, said the young journalist._

**En dashes** are not used as often, but are intended to be used for expressions
of range (time, numbers, etc.), most often as a replacement for the word "to",
and indicate that the values are inclusive:  
  &emsp;_Years 1900—2000._  
  &emsp;_The New York—San Francisco route._  
  &emsp;_The score was 27—17._

**Em dashes** are used for two primary purposes: 1. They are used to indicate
a stronger break in a sentence than commas or parentheses. 2. They are
used similarly to colons, but with a smidge more drama.

Em dashes in place of commas or parenthesis:  
  &emsp;_The 30th anniversary of the eruption of Mount St. Helens—May 18,
  1980—brought back vivid memories of ash and darkness._

Em dash in place of a colon:  
  &emsp;_There was only one thing missing from the pirate ship—pirates._

Em dashes are also used in citations, to indicate interruptions, to indicate
blotted out text, and more. But that won't be discussed here.

Read more about when to use hyphens, dashes, colons, parentheses&mdash;and
more&mdash;here:
- [Dashes, Colons, and Commas](https://www.quickanddirtytips.com/education/grammar/dashes-colons-and-commas)
- [Dashes, Parentheses, and Commas](https://www.quickanddirtytips.com/education/grammar/dashes-parentheses-and-commas)
- [Hyphens](https://www.quickanddirtytips.com/education/grammar/hyphens)
- [En Dash](https://www.thepunctuationguide.com/en-dash.html)
- [Em Dash](https://www.thepunctuationguide.com/em-dash.html)
- [Em Dash(—) vs. En Dash(–)](https://7esl.com/em-dash-en-dash/)

To see them mushed together for comparison . . .  
  &emsp;minus**hyphen**en dash**em dash**figure dash**quotation dash**:  
  &emsp;&minus;**&hyphen;**&ndash;**&mdash;**&#x2012;**&horbar;**  

For more information about the figure and quotation dashes (out of scope), read
these: [Figure Dash](https://en.wikipedia.org/wiki/Dash#Figure_dash), [Quotation
Dash](https://en.wikipedia.org/wiki/Quotation_mark#Quotation_dash).

We are going to focus on hyphens, and em and en dashes.

The Problem
-----------

If you write a piece that is more substantive than a short social-media post or
informal correspondence, em dashes are used quite frequently. En dashes are less
common, but used occasionally. The problem: There is no key on the keyboard for
the em, en dash, or minus sign (unless you have a numeric keypad). This can be
maddening.

The Hyphen
----------

Inputting the hyphen on your keyboard is easy. The _hyphen key_ is just to right
of the _0 key_ on most keyboards.

For most cases, the hyphen can be used in place of a minus sign, or even a
figure dash. If you are displaying some light arithmetic equations though, you
probably want to use the right character (the minus). Phone numbers generally
use figure dashes. And if you want to ensure a word is not word-wrapped (like in
a heading) the non-breaking hyphen is useful.

It should be noted that many people will just use hyphens in the place of en
dashes as well. And many editors will overlook this, but if you are writing more
formally, consider using the en dash instead.

Em Dashes in Word Processors
----------------------------

Inputting the em dash in a word processor _can be_ relatively easy. Most will
replace any `[-][-][space]` with `—`. If a particular word processor does not
enable this feature by default, look for it in the settings somewhere and enable
it if you like. I personally like to input these characters more directly from
the keyboard. More on that in a second. For the other characters, there is
usually a "Insert special character" selection in one of the menus.

Dashes in HTML- or Markdown-Formatted Documents
-----------------------------------------------

If you are creating an HTML- or Markdown-formatted document, a common method is
to use HTML ASCII or Unicode escape codes in the text. Some have human-readable
entity names: `&mdash;` and `&ndash;`.

For example, this document was originally written in the Markdown format. I
generally prefer to input the dashes directly from the keyboard, but it is also
very common to input them as HTML `&` escape codes. It's a very useful technique
to know.

More about Markdown can be found
[here](https://en.wikipedia.org/wiki/Markdown),
[here](https://commonmark.org/help/), and
[here](https://www.markdownguide.org/extended-syntax).

More about HTML ASCII escape codes can be found
[here](https://ascii.cl/htmlcodes.htm). You can use HTML escape codes in
Markdown documents, not just HTML-formatted files.

Markdown is widely used in many MANY programs now. Most note-taking
applications support it, some by default, or even nearly exclusively (example
[Joplin](https://joplinapp.org), my personal favorite). But also common forum
software ([Discourse](https://www.discourse.org/)). And many other platforms.

Dashes in the GNOME Desktop Environment
---------------------------------------

There are a myriad of ways to enable inputting of dashes in various operating
systems and desktop environments so that you can have a more flexible approach
inserting them no matter what application you are using. For the purposes of
this how-to, I am going to describe how to do it in GNOME, the default desktop
environment for many favors of Linux, to include Fedora, RHEL, and Ubuntu.

> For other environments (Apple, Microsoft, or Linux running KDE or very old
> GNOME) take a look at the article referenced at the end of this article.

### Compose Key Method

For these, a _Compose Key_ is used. In Fedora's GNOME environment it is not
enabled by default. Or, at least, it was not in my desktop settings. To enable
it, you need to install the "GNOME Tweak Tool", a package that gives you more
power over configuration of the desktop.

**Install GNOME Tweak Tool**

Install from the UI:
- Open the "Software" application
- Search for "GNOME Tweaks"
- Install

Install from the commandline:
- Fedora and EL8, RHEL8/CentOS8): `sudo dnf install gnome-tweaks -y`
- Ubuntu (I _believe_ this is correct): `sudo apt install gnome-tweak-tool`

**Enable and Map the Compose Key**

Now do this:
1. Open "Tweaks"
2. Select "Keyboard & Mouse"
3. Look for "Compose Key" and click on "Disabled"
4. Flip the switch from "OFF" to "ON"
5. Choose what you use for your compose key. I use "Caps Lock"  
   <span style="font-size: 75%;">_Note: whatever you choose, this setting will
   override any other use for that key._</span>

**Use the Compose Key**

Now open up a text editor (`gedit` will work, but any will do) and do this . . .

For an em dash (`[compose]`, then `---`), or
- `[compose key]` (in my case, the `[CAPS]` key)
- `[hyphen key]` (i.e., the hyphen key on the keyboard)
- `[hyphen key]`
- `[hyphen key]`

  _You should now see an em dash character (&mdash;)._

For an en dash (`[compose]`, then `--.`), or
- `[compose key]`
- `[hyphen key]`
- `[hyphen key]`
- `[period key]`

  _You should now see an en dash character (&ndash;)._

### Unicode Input Method

You can use the Unicode input method instead of using the compose key. It's a
bigger PITA and hard to remember, but useful to know so you can input other
Unicode characters when necessary:

- `[CTRL][SHIFT][U]`

  _An underlined "<span style="text-decoration: underline">u</span>" should
  appear._

- The Unicode for the character needed
- `[ENTER]`  
  <span style="font-size: 75%;">_Note: the `[ENTER]` at the end may or may not
  be necessary, depending on the environment and application._</span>

For example:
- Minus sign: (-): typically typed directly from keyboard.  
  <span style="font-size: 75%;">_or `[CTRL][SHIFT][U]`, then `002D[ENTER]`_</span>
- Hyphen (-): typically expressed by using the minus-sign from the keyboard.  
  <span style="font-size: 75%;">_or `[CTRL][SHIFT][U]`, then
  `2012[ENTER]`_</span>  
  <span style="font-size: 75%;">_or `[CTRL][SHIFT][U]`, then `2010[ENTER]` (the
  "breaking" version)._</span>
- En dash (–): `[CTRL][SHIFT][U]`, then `2013[ENTER]`
- Em dash (—): `[CTRL][SHIFT][U]`, then `2014[ENTER]`

A great summary of some of the most used `[CTRL][SHIFT][U]` Unicode input
codes can be found in the "Diacritics and punctuation" section of this article:
[Linux keyboard text symbols: Compose key
shortcuts](https://fsymbols.com/keyboard/linux/compose/).

An exhaustively comprehensive Unicode reference can be found here: [](https://unicode-table.com/)

Other Environments
------------------

Are you a Microsoft or Apple user? That's beyond the scope of this document, but
here's a good starting point: [5 Ways to Type a
Dash](https://www.wikihow.com/Type-a-Dash).

Happy Writing!
--------------

That's it! Good luck and enjoy your writing. Writing that aims to be more
exacting in its selection of dash-like punctuation.
