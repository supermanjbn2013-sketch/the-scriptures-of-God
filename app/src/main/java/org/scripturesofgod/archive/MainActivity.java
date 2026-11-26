package org.scripturesofgod.archive;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.view.Gravity;
import android.view.View;
import android.widget.*;
import android.text.TextWatcher;
import android.text.Editable;
import java.util.*;

public class MainActivity extends Activity {
    int bg=Color.rgb(15,19,24), panel=Color.rgb(26,33,41), gold=Color.rgb(205,174,112), ink=Color.rgb(232,228,217), muted=Color.rgb(160,166,170);
    LinearLayout root, content;
    String section="Home";
    boolean lightMode=false;
    String returnSection="Home";
    String previousSection="Home";
    void navigateTo(String destination){if(destination==null||destination.isEmpty())destination="Home";if(!destination.equals(section)){previousSection=section;section=destination;}show();}
    @Override public void onBackPressed(){if(!"Home".equals(section)){String destination=previousSection;previousSection="Home";section=destination;show();}else{super.onBackPressed();}}
    String[] translationNames={"Afrikaans","Arabic","Belarusian","Bulgarian","Bengali","Catalan","Czech","Welsh","Danish","German","Greek","English","Esperanto","Spanish","Estonian","Persian","Finnish","French","Irish","Galician","Gujarati","Hebrew","Hindi","Croatian","Haitian Creole","Hungarian","Indonesian","Icelandic","Italian","Japanese","Georgian","Kannada","Korean","Lithuanian","Latvian","Macedonian","Marathi","Malay","Maltese","Dutch","Norwegian","Polish","Portuguese","Romanian","Russian","Slovak","Slovenian","Albanian","Swedish","Swahili","Tamil","Telugu","Thai","Filipino / Tagalog","Turkish","Ukrainian","Urdu","Vietnamese","Chinese"};
    String[] translationCodes={"af","ar","be","bg","bn","ca","cs","cy","da","de","el","en","eo","es","et","fa","fi","fr","ga","gl","gu","he","hi","hr","ht","hu","id","is","it","ja","ka","kn","ko","lt","lv","mk","mr","ms","mt","nl","no","pl","pt","ro","ru","sk","sl","sq","sv","sw","ta","te","th","tl","tr","uk","ur","vi","zh"};
    String targetLanguage(){return getSharedPreferences("archive_settings",MODE_PRIVATE).getString("target_language","en");}
    String targetLanguageName(){String code=targetLanguage();for(int i=0;i<translationCodes.length;i++)if(translationCodes[i].equals(code))return translationNames[i];return "English";}
    void showTranslationSettings(){String[] items={"Connect Gemini API key","Choose target language ("+targetLanguageName()+")","How translation works"};new android.app.AlertDialog.Builder(this).setTitle("AI translation connection").setItems(items,(d,w)->{if(w==0)openAiConnectionSettings();else if(w==1)chooseTranslationLanguage();else showInfo("Gemini AI translation","This app uses only the Gemini API for AI translation. Save your own Gemini API key once; it is encrypted on this device and reused. Your selected target language is remembered automatically. Internet access is required when you request a translation.");}).show();}
    void openAiConnectionSettings(){Intent intent=new Intent(this,AiTranslatorActivity.class);intent.putExtra("open_connection_settings",true);intent.putExtra("preferred_target_language",targetLanguageName());startActivity(intent);}
    void chooseTranslationLanguage(){
        int selected=0;for(int i=0;i<translationCodes.length;i++)if(translationCodes[i].equals(targetLanguage()))selected=i;
        new android.app.AlertDialog.Builder(this).setTitle("Preferred translation language").setMessage("Choose the language Gemini AI should use when you request a translation. Your selection is saved on this device.").setSingleChoiceItems(translationNames,selected,(dialog,which)->{
            getSharedPreferences("archive_settings",MODE_PRIVATE).edit().putString("target_language",translationCodes[which]).apply();
            dialog.dismiss();show();
        }).setNegativeButton("Cancel",null).show();
    }
    Map<String,ArrayList<String>> entries=new LinkedHashMap<>();
    String[] sections={"Home","Hebrew Scriptures","DSS Hebrew Archive","Prophets","Unified Apostolic and Disciple Writings","Apocrypha and Deuterocanonical Writings","Writings Mentioned in the Scriptures","Lost and Referenced Books","Other Reference Books","Manuscript Archive","DSS Archive","Papyrus Archive","Codex Vaticanus Archive","Codex Sinaiticus Archive","DSS Passage Concordance","DSS Transcription Archive","Translation Center","Manuscript Comparison","Research Archive","Favorites","Reading History","Personal Library","Settings"};
    @Override public void onCreate(Bundle b){super.onCreate(b); applyTheme(); seed(); show();}
    void applyTheme(){String mode=getSharedPreferences("archive_settings",MODE_PRIVATE).getString("theme","dark");lightMode=mode.equals("light")||(mode.equals("system")&&((getResources().getConfiguration().uiMode&android.content.res.Configuration.UI_MODE_NIGHT_MASK)==android.content.res.Configuration.UI_MODE_NIGHT_NO));if(lightMode){bg=Color.rgb(247,245,239);panel=Color.rgb(255,255,255);gold=Color.rgb(133,94,38);ink=Color.rgb(35,39,42);muted=Color.rgb(105,110,113);}else{bg=Color.rgb(15,19,24);panel=Color.rgb(26,33,41);gold=Color.rgb(205,174,112);ink=Color.rgb(232,228,217);muted=Color.rgb(160,166,170);}}
    void saveTheme(String mode){getSharedPreferences("archive_settings",MODE_PRIVATE).edit().putString("theme",mode).apply();applyTheme();show();}
    void openSettings(){String[] items={"System default","Light","Dark","Reading font size","Preferred translation language","About this application","Privacy information"};new android.app.AlertDialog.Builder(this).setTitle("Settings").setItems(items,(d,w)->{if(w==0)saveTheme("system");else if(w==1)saveTheme("light");else if(w==2)saveTheme("dark");else if(w==3)chooseFontSize();else if(w==4)chooseTranslationLanguage();else if(w==5)showInfo("About","The Scriptures of God is an offline-first Scripture and manuscript research archive. Texts are displayed with source and edition attribution.");else showInfo("Privacy","Reading history, bookmarks, notes, preferred language and the encrypted Gemini API key are stored locally on this device. When you request AI translation, the submitted passage is sent to Google Gemini over the internet.");}).show();}
    void chooseFontSize(){int size=getSharedPreferences("archive_settings",MODE_PRIVATE).getInt("font_size",16);final SeekBar bar=new SeekBar(this);bar.setMax(16);bar.setProgress(Math.max(0,Math.min(16,size-12)));new android.app.AlertDialog.Builder(this).setTitle("Reading font size").setMessage("Adjust passage text size").setView(bar).setPositiveButton("Save",(d,w)->getSharedPreferences("archive_settings",MODE_PRIVATE).edit().putInt("font_size",12+bar.getProgress()).apply()).setNegativeButton("Cancel",null).show();}
    void showInfo(String title,String message){new android.app.AlertDialog.Builder(this).setTitle(title).setMessage(message).setPositiveButton("Close",null).show();}
    void enablePassageSelection(TextView view){
        view.setTextIsSelectable(true);
        view.setCustomSelectionActionModeCallback(new android.view.ActionMode.Callback(){
            public boolean onCreateActionMode(android.view.ActionMode mode,android.view.Menu menu){
                menu.add(0,7342,10,"Select all");
                menu.add(0,7343,20,"Copy");
                menu.add(0,7344,30,"Highlight selected");
                menu.add(0,7341,40,"Translate selected text").setShowAsAction(android.view.MenuItem.SHOW_AS_ACTION_IF_ROOM);
                return true;
            }
            public boolean onPrepareActionMode(android.view.ActionMode mode,android.view.Menu menu){return true;}
            public boolean onActionItemClicked(android.view.ActionMode mode,android.view.MenuItem item){
                int id=item.getItemId();
                if(id==7342){if(view.getText() instanceof android.text.Spannable){android.text.Selection.selectAll((android.text.Spannable)view.getText());}return true;}
                int start=view.getSelectionStart(),end=view.getSelectionEnd();
                if(start<0||end<0||start==end){Toast.makeText(MainActivity.this,"Select text first.",Toast.LENGTH_SHORT).show();return true;}
                String selected=view.getText().subSequence(Math.min(start,end),Math.max(start,end)).toString().trim();
                if(selected.isEmpty())return true;
                if(id==7343){((android.content.ClipboardManager)getSystemService(CLIPBOARD_SERVICE)).setPrimaryClip(android.content.ClipData.newPlainText("Selected passage",selected));Toast.makeText(MainActivity.this,"Selected text copied.",Toast.LENGTH_SHORT).show();mode.finish();return true;}
                if(id==7344){String reference=view.getTag()==null?"Selected passage":String.valueOf(view.getTag());appendLibraryEntry("highlights",reference+"  "+selected);Toast.makeText(MainActivity.this,"Selected text highlighted and saved.",Toast.LENGTH_SHORT).show();mode.finish();return true;}
                if(id!=7341)return false;
                String sourceLanguage="auto";if(selected.matches("(?s).*[֐-׿].*"))sourceLanguage="he";else if(selected.matches("(?s).*[Ͱ-Ͽ].*"))sourceLanguage="grc";
                Intent intent=new Intent(MainActivity.this,AiTranslatorActivity.class);intent.putExtra("passage_text",selected);intent.putExtra("source_language",sourceLanguage);intent.putExtra("preferred_target_language",targetLanguageName());startActivity(intent);mode.finish();return true;
            }
            public void onDestroyActionMode(android.view.ActionMode mode){}
        });
    }

    void seed(){
        entries.put("Hebrew Scriptures",new ArrayList<>(Arrays.asList("Genesis","Exodus","Leviticus","Numbers","Deuteronomy","Joshua","Judges","Ruth","1 Samuel","2 Samuel","1 Kings","2 Kings","1 Chronicles","2 Chronicles","Ezra","Nehemiah","Esther","Job","Psalms","Proverbs","Ecclesiastes","Song of Songs","Isaiah","Jeremiah","Lamentations","Ezekiel","Daniel","Hosea","Joel","Amos","Obadiah","Jonah","Micah","Nahum","Habakkuk","Zephaniah","Haggai","Zechariah","Malachi")));
        entries.put("Prophets",new ArrayList<>(Arrays.asList("Isaiah","Jeremiah","Ezekiel","Daniel","Hosea","Joel","Amos","Obadiah","Jonah","Micah","Nahum","Habakkuk","Zephaniah","Haggai","Zechariah","Malachi")));
        entries.put("Disciples and Apostles Writings",new ArrayList<>(Arrays.asList("Matthew","Mark","Luke","John","Acts","Romans","1 Corinthians","2 Corinthians","Galatians","Ephesians","Philippians","Colossians","1 Thessalonians","2 Thessalonians","1 Timothy","2 Timothy","Titus","Philemon","Hebrews","James","1 Peter","2 Peter","1 John","2 John","3 John","Jude","Revelation")));
        entries.put("Apocrypha and Deuterocanonical Writings",new ArrayList<>(Arrays.asList("1 Esdras","Tobit","Judith","Esther (Greek)","Wisdom of Solomon","Sirach","Baruch","Letter of Jeremiah","1 Maccabees","2 Maccabees","3 Maccabees","4 Maccabees","Susanna (Old Greek)","Susanna (Theodotion)","Daniel (Old Greek)","Daniel (Theodotion)","Bel and the Dragon (Old Greek)","Bel and the Dragon (Theodotion)","Odes","Prayer of Manasseh (Greek)","Psalm 151","2 Esdras / 4 Ezra (Latin)","Prayer of Manasseh (Latin)")));
        entries.put("Writings Mentioned in the Scriptures",new ArrayList<>(Arrays.asList("Book of the Wars of the LORD","Book of Jashar","Records of Samuel, Nathan, and Gad","Paul's Earlier Letter to Corinth","Paul's Severe / Sorrowful Letter to Corinth","Letter Associated with Laodicea","Prophecy / Book of Enoch (1 Enoch)")));
        entries.put("Early Disciple and Apostolic Writings",new ArrayList<>(Arrays.asList("Epistle of Barnabas","Shepherd of Hermas","1 Clement","2 Clement","Didache","Letters of Ignatius of Antioch")));
        entries.put("Early Christian Gospels and Related Writings",new ArrayList<>(Arrays.asList("Gospel of Peter","Gospel of Thomas","Gospel of Mary","Apocalypse of Peter")));
        entries.put("Other Reference Books",new ArrayList<>(Arrays.asList("Jubilees","Protoevangelium of James (Nativity and Infancy of Jesus)","Infancy Gospel of Thomas","Gospel of Pseudo-Matthew","Arabic Infancy Gospel","Gospel of Philip","Gospel of Truth","Gospel of Judas","Acts of Peter","Acts of Paul","Acts of John","Acts of Thomas","Apocalypse of Paul","Ascension of Isaiah","Testament of Abraham","Testament of the Twelve Patriarchs","2 Baruch","3 Baruch","Life of Adam and Eve","Apocalypse of Moses","Dormition of Mary (Transitus Mariae traditions)","Six Books Dormition Apocryphon","Book of Mary's Repose","Odes of Solomon","Pseudo-Philo: Biblical Antiquities","Zohar")));
        entries.put("Lost and Referenced Books",new ArrayList<>(Arrays.asList("Acts of Solomon","Chronicles of the Kings of Israel","Chronicles of the Kings of Judah","Prophecy of Ahijah","Visions of Iddo","Records of Shemaiah","Records of Iddo","History of Iddo","Book of Jehu","Records of the Seers (Hozai)","Chronicles of the Kings of Media and Persia","Assumption of Moses (identification debated)","Book of Noah (Jubilees reference)","Book of Giants (fragmentarily preserved)","Nehemiah's Library and Collected Records","Jason of Cyrene's Five-Book History","Chronicles of John Hyrcanus","Book of Laments for Josiah","Chronicles of King David","Samuel's Book of the Kingdom","Records of Samuel the Seer","Records of Nathan the Prophet","Records of Gad the Seer","Words or Records of the Kings of Israel","Commentary (Midrash) on the Book of Kings","Writings or Decrees of David and Solomon","Book of the Kings of Israel (Chronicles source)","Annals of the Kings of Israel (Manasseh source)","Book of the Kings of Judah and Israel","Book of the Kings of Israel and Judah","Chronicles of the Levites","Epistle to the Alexandrians (Muratorian Fragment)","Marcionite Epistle to the Laodiceans (Muratorian Fragment)","Marcionite Book of Psalms (unnamed collection)")));
        entries.put("Manuscript Archive",new ArrayList<>(Arrays.asList("Dead Sea Scrolls (DSS)","Great Isaiah Scroll (1QIsaᵃ)","Pesher Habakkuk (1QpHab)","Genesis Apocryphon (1QapGen)","Community Rule (1QS)","Temple Scroll (11Q19)","War Scroll (1QM)","Masoretic Text","Septuagint","Samaritan Pentateuch","Papyrus 46 (P46)","Papyrus 52 (P52)","Papyrus 66 (P66)","Papyrus 72 (P72)","Papyrus 75 (P75)","Papyrus 76 (P76)","Papyrus 77 (P77)","Codex Vaticanus","Codex Sinaiticus","Codex Alexandrinus")));
        entries.put("DSS Archive",new ArrayList<>(Arrays.asList("Great Isaiah Scroll (1QIsaᵃ)","Pesher Habakkuk (1QpHab)","Genesis Apocryphon (1QapGen)","Community Rule (1QS)","Temple Scroll (11Q19)","War Scroll (1QM)")));
        entries.put("Papyrus Archive",new ArrayList<>(Arrays.asList("Papyrus 46 (P46)","Papyrus 52 (P52)","Papyrus 66 (P66)","Papyrus 72 (P72)","Papyrus 75 (P75)","Papyrus 76 (P76)","Papyrus 77 (P77)","Papyrus 103 (P103)","Papyrus 104 (P104)","Papyrus 45 (P45)","Papyrus 88 (P88)")));
        entries.put("Codex Vaticanus Archive",new ArrayList<>(Arrays.asList("Codex Vaticanus (GA 03)")));
        entries.put("Codex Sinaiticus Archive",new ArrayList<>(Arrays.asList("Codex Sinaiticus (GA 01)")));
        entries.put("DSS Passage Concordance",new ArrayList<>(Arrays.asList("4Q26 Lev d — Leviticus","4Q27 Num b — Numbers","4Q31 Deut d — Deuteronomy","4Q47 Josh a — Joshua","4Q53 Sam c — Samuel")));
        entries.put("Translation Center",new ArrayList<>(Arrays.asList("Preferred translation language","Gemini AI translation")));
        entries.put("Manuscript Comparison",new ArrayList<>(Arrays.asList("Compare witness transcriptions","Review additions and omissions","Inspect textual variants","Trace quotations and parallels")));
        entries.put("Research Archive",new ArrayList<>(Arrays.asList("Source metadata","Authorship assessments","Composition dates","Language and provenance","Fragment and witness records","Research notes")));
        entries.put("Favorites",new ArrayList<>()); entries.put("Reading History",new ArrayList<>());
    }
    GradientDrawable shape(int color){GradientDrawable d=new GradientDrawable();d.setColor(color);d.setCornerRadius(18);return d;}
    TextView text(String s,int size,int color,boolean bold){TextView t=new TextView(this);t.setText(s);t.setTextSize(size);t.setTextColor(color);if(bold)t.setTypeface(Typeface.DEFAULT,Typeface.BOLD);t.setPadding(16,12,16,12);return t;}
    void show(){
        root=new LinearLayout(this);root.setOrientation(1);root.setBackgroundColor(bg);
        ScrollView scroll=new ScrollView(this); LinearLayout page=new LinearLayout(this);page.setOrientation(1);page.setPadding(16,18,16,24);scroll.addView(page);
        LinearLayout brandRow=new LinearLayout(this);brandRow.setGravity(Gravity.CENTER_VERTICAL);if(!"Home".equals(section)){TextView back=text("‹ Back",16,gold,true);back.setOnClickListener(v->onBackPressed());brandRow.addView(back);}TextView brand=text("THE SCRIPTURES OF GOD",20,gold,true);brandRow.addView(brand,new LinearLayout.LayoutParams(0,-2,1));TextView settings=text("⚙",24,ink,true);settings.setOnClickListener(v->openSettings());brandRow.addView(settings);page.addView(brandRow);
        page.addView(text("Ancient Manuscript Archive  ·  Scripture Research",12,muted,false));
        EditText search=new EditText(this);search.setSingleLine(true);search.setTextColor(ink);search.setHintTextColor(muted);search.setHint("Search exact word or phrase, reference, manuscript…");search.setPadding(16,10,16,10);search.setBackground(shape(panel));LinearLayout.LayoutParams sp=new LinearLayout.LayoutParams(-1,-2);sp.setMargins(0,18,0,14);page.addView(search,sp);
        Button corpusSearch=new Button(this);corpusSearch.setText("Search complete text corpus");corpusSearch.setTextColor(ink);corpusSearch.setBackground(shape(panel));page.addView(corpusSearch,new LinearLayout.LayoutParams(-1,-2));
        corpusSearch.setOnClickListener(v->{String query=search.getText().toString().trim();if(query.length()>0)searchCorpus(query);});
        Button languageButton=new Button(this);languageButton.setText("Translation connection settings · Target: "+targetLanguageName());languageButton.setTextColor(gold);languageButton.setBackground(shape(panel));LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,-2);lp.setMargins(0,8,0,12);page.addView(languageButton,lp);languageButton.setOnClickListener(v->showTranslationSettings());
        content=new LinearLayout(this);content.setOrientation(1);page.addView(content);
        search.addTextChangedListener(new TextWatcher(){public void beforeTextChanged(CharSequence s,int st,int c,int a){} public void onTextChanged(CharSequence s,int st,int before,int count){render(s.toString());}public void afterTextChanged(Editable e){}});
        render("");root.addView(scroll,new LinearLayout.LayoutParams(-1,0,1));
        HorizontalScrollView navScroll=new HorizontalScrollView(this);LinearLayout nav=new LinearLayout(this);nav.setPadding(8,8,8,8);nav.setBackgroundColor(panel);
        for(String s:sections){TextView b=text(s,12,s.equals(section)?gold:ink,true);b.setOnClickListener(v->navigateTo(s));nav.addView(b);}navScroll.addView(nav);root.addView(navScroll,new LinearLayout.LayoutParams(-1,-2));
        setContentView(root);
    }
    void addHomeTile(String title,String subtitle,Runnable action){LinearLayout tile=new LinearLayout(this);tile.setOrientation(1);tile.setPadding(14,8,14,8);tile.setBackground(shape(panel));TextView heading=text(title,16,ink,true);heading.setPadding(2,4,2,2);TextView sub=text(subtitle,12,muted,false);sub.setPadding(2,0,2,4);tile.addView(heading);tile.addView(sub);LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,-2);p.setMargins(0,6,0,6);content.addView(tile,p);tile.setOnClickListener(v->action.run());}
    void render(String q){
        content.removeAllViews();
        content.addView(text(section,22,ink,true));
        if(section.equals("Home")){
            content.addView(text("READ  •  SEARCH  •  COMPARE",12,gold,true));
            TextView hero=text("Return to the words.\nExplore the witnesses.",25,ink,true);hero.setBackground(shape(panel));content.addView(hero);
            String last=getSharedPreferences("archive_library",MODE_PRIVATE).getString("last_book","");
            TextView resume=text(last.isEmpty()?"Begin reading":"Continue reading  ·  "+last,16,ink,true);resume.setBackground(shape(panel));LinearLayout.LayoutParams rp=new LinearLayout.LayoutParams(-1,-2);rp.setMargins(0,10,0,10);content.addView(resume,rp);resume.setOnClickListener(v->{if(!last.isEmpty()){returnSection="Home";openBook(last);}else{navigateTo("Hebrew Scriptures");}});
            TextView searchTile=text("⌕   Search the Scriptures and manuscript records",15,ink,true);searchTile.setBackground(shape(panel));content.addView(searchTile);searchTile.setOnClickListener(v->navigateTo("Search"));
            content.addView(text("SCRIPTURE COLLECTIONS",12,gold,true));
            addHomeTile("Hebrew Scriptures","39 writings",() -> navigateTo("Hebrew Scriptures"));
            addHomeTile("DSS Hebrew Archive","Hebrew Scripture books, DSS-preserved apocrypha, and referenced writings — manuscript text only",() -> navigateTo("DSS Hebrew Archive"));
            addHomeTile("Unified Apostolic and Disciple Writings","All catalogued letters, gospels, acts, testimony and related works in estimated chronological order",() -> navigateTo("Unified Apostolic and Disciple Writings"));
            addHomeTile("Apocrypha and Deuterocanonical Writings","Greek and Latin textual forms",() -> navigateTo("Apocrypha and Deuterocanonical Writings"));
            addHomeTile("Lost and Referenced Books","Other ancient records, fragmentary works and disputed identifications",() -> navigateTo("Lost and Referenced Books"));
            addHomeTile("Other Reference Books","Ancient Jewish and early Christian writings outside the main Scripture collections",() -> navigateTo("Other Reference Books"));
            content.addView(text("MANUSCRIPT RESEARCH",12,gold,true));
            addHomeTile("Dead Sea Scrolls Archive","Dedicated archive for DSS manuscripts and transcriptions",() -> navigateTo("DSS Archive"));
            addHomeTile("Papyrus Archive","Greek papyrus witnesses, transcriptions and English readings",() -> navigateTo("Papyrus Archive"));
            addHomeTile("Codex Vaticanus Archive","Dedicated archive for Codex Vaticanus witness text",() -> navigateTo("Codex Vaticanus Archive"));
            addHomeTile("DSS Transcription Archive","Offline line-level readings from the ETCBC / Abegg corpus",() -> navigateTo("DSS Transcription Archive"));
            addHomeTile("Greek Manuscripts","Papyrus and codex registers",()->{section="Manuscript Archive";show();});
            addHomeTile("Latin Manuscripts","Latin transmission records",()->{section="Manuscript Archive";show();});
            addHomeTile("Manuscript Research Library","Sources, provenance and textual forms",() -> navigateTo("Research Archive"));
            content.addView(text("PERSONAL LIBRARY",12,gold,true));
            addHomeTile("Bookmarks and Reading History","Your saved passages on this device",() -> navigateTo("Personal Library"));
            return;
        }
        if(section.equals("Settings")){content.addView(text("Appearance, reading and privacy",14,muted,false));addHomeTile("Appearance and reading settings","Theme, font size and language",()->openSettings());return;}
        if(section.equals("Personal Library")||section.equals("Favorites")||section.equals("Reading History")){renderLibrary();return;}
        if(section.equals("Search")){EditText query=new EditText(this);query.setSingleLine(true);query.setHint("Exact word or phrase");content.addView(query);Button go=new Button(this);go.setText("Search offline corpus");content.addView(go);go.setOnClickListener(v->{String searchTerm=query.getText().toString().trim();if(!searchTerm.isEmpty())searchCorpus(searchTerm);});return;}
        if(section.equals("Manuscript Comparison")){
            content.addView(text("JOHN · GREEK MANUSCRIPT COMPARISON",12,gold,true));
            content.addView(text("Compare the imported diplomatic transcriptions by chapter and verse. Each witness remains separate; spelling, supplied letters, and correction notes are not silently harmonized.",14,muted,false));
            Button compare=new Button(this);compare.setText("Compare a John passage");compare.setTextColor(ink);compare.setBackground(shape(panel));content.addView(compare,new LinearLayout.LayoutParams(-1,-2));
            compare.setOnClickListener(v->openJohnWitnessComparison());
            content.addView(text("Available indexed witnesses: P52, P66, P75, Codex Vaticanus, and Codex Sinaiticus. A missing entry is not automatically proof of a textual omission; the manuscript page and source apparatus must be checked.",12,muted,false));
            return;
        }
        if(section.equals("DSS Transcription Archive")){renderEtcbcDssIndex(q);return;}
        if(section.equals("DSS Hebrew Archive")){renderDssHebrewArchive(q);return;}
        if(section.equals("Papyrus Archive")){content.addView(text("GREEK PAPYRUS WITNESSES",12,gold,true));content.addView(text("Each papyrus is a separate physical witness. A fragment's passage coverage is not a complete book. Open a witness to inspect its surviving transcription and source record.",13,muted,false));}
        if(section.equals("Codex Vaticanus Archive")){content.addView(text("CODEX VATICANUS · GA 03",12,gold,true));content.addView(text("This archive contains the Codex Vaticanus transcription independently of other manuscript archives. Only the witness text is shown; missing leaves are not silently filled.",13,muted,false));}
        if(section.equals("DSS Archive")){content.addView(text("DEAD SEA SCROLLS · QUMRAN MANUSCRIPTS",12,gold,true));content.addView(text("This archive is limited to actual DSS witnesses and their source records. A scroll's preserved text is distinguished from restored or missing portions.",13,muted,false));}
        if(section.equals("Unified Apostolic and Disciple Writings")){renderUnifiedWritings(q);return;}
        if(section.equals("Writings Mentioned in the Scriptures")){content.addView(text("SCRIPTURE REFERENCES • LOST SOURCES • RECOVERED WITNESSES",12,gold,true));content.addView(text("This catalogue separates a writing named in a surviving passage from any surviving manuscript of that writing. Lost works remain reference records only. Fragmentary and translated works show their actual witnesses and language. 1 Enoch is included as a recovered work quoted in Jude, not as a lost book.",14,muted,false));}
        if(section.equals("Early Disciple and Apostolic Writings")){content.addView(text("EARLY CHRISTIAN WRITINGS • CODEX CONTENTS • PAPYRUS WITNESSES",12,gold,true));content.addView(text("These works survive in different manuscripts, dates, languages and textual forms. Their presence in a codex is a historical fact about that manuscript, not by itself a ruling about scriptural authority.",14,muted,false));}
        if(section.equals("Early Christian Gospels and Related Writings")){content.addView(text("GREEK PAPYRI • COPTIC CODEXES • ETHIOPIC TRANSMISSION",12,gold,true));content.addView(text("Each manuscript witness is listed separately. Short fragments are not silently joined into a complete text, and later translations are not mislabelled as early Greek manuscripts.",14,muted,false));}
        if(section.equals("Other Reference Books")){content.addView(text("ANCIENT JEWISH • EARLY CHRISTIAN • LATER MYSTICAL WRITINGS",12,gold,true));content.addView(text("This separate archive catalogs surviving and fragmentary writings outside the main Scripture collections. Inclusion is for reference and historical study; it does not automatically establish scriptural authority or make a work part of the Scripture collections. Manuscript forms and dates are identified separately.",14,muted,false));}
        if(section.equals("Lost and Referenced Books")){content.addView(text("ANCIENT SOURCES • LOST RECORDS • FRAGMENTARY WRITINGS",12,gold,true));content.addView(text("This archive indexes writings named or cited by surviving ancient works. Each entry identifies its source reference and whether the work is lost, fragmentarily preserved, unidentified, or disputed. A reference is not the lost book itself; missing contents are never invented.",14,muted,false));}
        ArrayList<String> data=entries.get(section); if(data==null)data=new ArrayList<>();
        int count=0;for(String item:data){if(q.length()==0||item.toLowerCase().contains(q.toLowerCase())){TextView row=text(item,15,ink,false);row.setBackground(shape(panel));LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,-2);p.setMargins(0,5,0,5);content.addView(row,p); row.setOnClickListener(v -> {returnSection=section;if(section.equals("Writings Mentioned in the Scriptures")){if(item.equals("Book of the Wars of the LORD")||item.equals("Book of Jashar")||item.equals("Records of Samuel, Nathan, and Gad")||item.equals("Paul's Earlier Letter to Corinth")||item.equals("Paul's Severe / Sorrowful Letter to Corinth")||item.equals("Letter Associated with Laodicea"))openReferencedBookEntry(item);else openHistoricalWritingEntry(item);}else if(section.equals("Early Disciple and Apostolic Writings")||section.equals("Early Christian Gospels and Related Writings"))openHistoricalWritingEntry(item);else if(section.equals("Lost and Referenced Books"))openReferencedBookEntry(item);else if(section.equals("Other Reference Books"))openOtherReferenceBookEntry(item);else if(section.equals("Translation Center")){if(item.equals("Preferred translation language"))chooseTranslationLanguage();else openAiConnectionSettings();}else if(section.equals("DSS Passage Concordance"))openDssConcordanceEntry(item);else if(section.equals("Papyrus Archive")){if(item.contains("46"))openPapyrus46Archive();else if(item.contains("52"))openPapyrus52Archive();else openCatalogEntry(item);}else if(section.equals("Codex Vaticanus Archive"))openVaticanusArchive();else if(codeFor(item)!=null)openBook(item);else if(section.equals("DSS Archive")||item.toLowerCase().contains("isaiah scroll")||item.toLowerCase().contains("habakkuk")||item.toLowerCase().contains("genesis apocryphon")||item.toLowerCase().contains("community rule")||item.toLowerCase().contains("temple scroll")||item.toLowerCase().contains("war scroll"))openDssCatalogEntry(item);else openCatalogEntry(item);}); count++;}}
        if(count==0)content.addView(text("No matching entries. This archive does not fabricate missing manuscript contents or readings.",14,muted,false));
        if(section.equals("Manuscript Archive")||section.equals("Research Archive")||section.equals("Manuscript Comparison"))content.addView(text("Records are catalog placeholders until a source, transcription, date and provenance are verified and attached.",12,gold,false));
    }


    void renderUnifiedWritings(String query){
        try{
            java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("catalog/unified_apostolic_disciple_writings.json"),"UTF-8"));
            StringBuilder raw=new StringBuilder();String line;while((line=reader.readLine())!=null)raw.append(line);reader.close();
            org.json.JSONArray records=new org.json.JSONObject(raw.toString()).getJSONArray("records");
            java.util.ArrayList<org.json.JSONObject> ordered=new java.util.ArrayList<>();
            for(int i=0;i<records.length();i++)ordered.add(records.getJSONObject(i));
            java.util.Collections.sort(ordered,(a,b)->{int p=Integer.compare(a.optInt("historical_sequence",999),b.optInt("historical_sequence",999));if(p!=0)return p;int q=Integer.compare(a.optInt("historical_subsequence",999),b.optInt("historical_subsequence",999));return q!=0?q:a.optString("title","").compareToIgnoreCase(b.optString("title",""));});
            int shown=0;
            for(org.json.JSONObject record:ordered){
                String title=record.optString("title","Untitled record");
                String hay=(title+" "+record.optString("description","")+" "+record.optString("genre","")+" "+record.optString("attribution_status","")+" "+record.optString("textual_status","")).toLowerCase(java.util.Locale.ROOT);
                if(!query.isEmpty()&&!hay.contains(query.toLowerCase(java.util.Locale.ROOT)))continue;
                TextView titleView=text(title,16,ink,true);
                titleView.setPadding(14,13,14,13);
                titleView.setBackground(shape(panel));
                LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,-2);lp.setMargins(0,3,0,3);
                content.addView(titleView,lp);
                titleView.setOnClickListener(v->showUnifiedWritingDetail(record));
                shown++;
            }
            if(shown==0)content.addView(text("No matching writing titles.",14,muted,false));
        }catch(Exception e){content.addView(text("The unified writings catalogue could not be opened: "+e.getMessage(),13,muted,false));}
    }

    void showUnifiedWritingDetail(org.json.JSONObject record){
        showUnifiedWritingStudy(record);
    }

    void showUnifiedEnglishReading(org.json.JSONObject record){
        String writingId=record.optString("id","");
        String title=record.optString("title","Writing");
        try{
            java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("catalog/unified_readings.json"),"UTF-8"));
            StringBuilder raw=new StringBuilder();String line;
            while((line=reader.readLine())!=null)raw.append(line);
            reader.close();
            org.json.JSONObject rootObject=new org.json.JSONObject(raw.toString());
            org.json.JSONArray readings=rootObject.optJSONArray("readings");
            org.json.JSONObject selected=null;
            if(readings!=null)for(int i=0;i<readings.length();i++){
                org.json.JSONObject candidate=readings.optJSONObject(i);
                if(candidate!=null&&writingId.equals(candidate.optString("writing_id",""))){selected=candidate;break;}
            }
            if(selected==null||selected.optString("english_text","").trim().isEmpty()){
                showInfo("English reading not yet complete",
                    "The complete English reading for "+title+" has not yet been added and verified. This entry currently contains research and manuscript records only. No missing wording will be invented or silently filled.");
                return;
            }
            String readingText=selected.optString("english_text","");
            TextView heading=text(title,21,gold,true);
            TextView status=text("Working translation — manuscript collation is not yet complete.",13,muted,false);
            TextView passage=text(readingText,18,ink,false);
            enablePassageSelection(passage);
            passage.setLineSpacing(5f,1.12f);
            int fontSize=getSharedPreferences("archive_settings",MODE_PRIVATE).getInt("font_size",18);
            passage.setTextSize(fontSize);
            LinearLayout readingLayout=new LinearLayout(this);
            readingLayout.setOrientation(1);
            readingLayout.setPadding(8,8,8,16);
            readingLayout.addView(heading);
            readingLayout.addView(status);
            readingLayout.addView(passage);
            ScrollView scroll=new ScrollView(this);
            scroll.setPadding(10,8,10,8);
            scroll.addView(readingLayout);
            String attribution=selected.optString("source_note","");
            if(!selected.optString("text_basis","").isEmpty())attribution+="\\n\\nText basis: "+selected.optString("text_basis");
            if(!selected.optString("translation_basis","").isEmpty())attribution+="\\n\\nTranslation basis: "+selected.optString("translation_basis");
            org.json.JSONArray segments=selected.optJSONArray("segments");
            if(segments!=null&&segments.length()>0){
                attribution+="\\n\\nChapter-by-chapter source and editorial notes:";
                for(int i=0;i<segments.length();i++){
                    org.json.JSONObject segment=segments.optJSONObject(i);if(segment==null)continue;
                    attribution+="\\n\\n"+segment.optString("passage_reference",segment.optString("segment_id","Chapter"));
                    attribution+="\\nStatus: "+segment.optString("segment_status","Not stated");
                    for(String key:new String[]{"source_witness_id","source_location","transcription_or_edition_basis","editorial_note"}){
                        String value=segment.optString(key,"");if(!value.isEmpty())attribution+="\\n"+key.replace("_"," ")+": "+value;
                    }
                }
            }
            org.json.JSONArray pending=selected.optJSONArray("witnesses_pending");
            if(pending!=null&&pending.length()>0){attribution+="\\n\\nWitness collation still pending:";for(int i=0;i<pending.length();i++){org.json.JSONObject witness=pending.optJSONObject(i);if(witness!=null)attribution+="\\n"+witness.optString("id")+": "+witness.optString("task");}}
            if("john".equals(writingId)){
                showJohnChapterReader(title,readingText,attribution);
                return;
            }
            android.app.AlertDialog.Builder builder=new android.app.AlertDialog.Builder(this)
                .setTitle("English reading")
                .setView(scroll)
                .setPositiveButton("Close",null);
            final String attributionText=attribution;
            if(!attributionText.isEmpty())builder.setNeutralButton("Text source",(dialog,which)->showInfo("Reading source",attributionText));
            builder.show();
        }catch(Exception e){
            showInfo("English reading not yet available",
                "The separate reading-text archive could not provide a verified complete English text for "+title+". Research descriptions and manuscript notes are not substituted for the actual reading.");
        }
    }

    void showJohnChapterReader(String title,String readingText,String attribution){
        java.util.ArrayList<String> chapterTexts=new java.util.ArrayList<>();
        java.util.regex.Matcher matcher=java.util.regex.Pattern.compile("(?m)^John (\\d+)\\s*$").matcher(readingText);
        java.util.ArrayList<Integer> starts=new java.util.ArrayList<>();
        java.util.ArrayList<Integer> numbers=new java.util.ArrayList<>();
        while(matcher.find()){starts.add(matcher.start());numbers.add(Integer.parseInt(matcher.group(1)));}
        for(int i=0;i<starts.size();i++){
            int end=i+1<starts.size()?starts.get(i+1):readingText.length();
            chapterTexts.add(readingText.substring(starts.get(i),end).trim());
        }
        if(chapterTexts.isEmpty()){
            showInfo("John chapter index unavailable","The chapter headings could not be identified in the reading text.");
            return;
        }
        final int[] selected={0};
        LinearLayout reader=new LinearLayout(this);
        reader.setOrientation(1);
        reader.setPadding(10,8,10,8);
        reader.addView(text("SELECT A CHAPTER",12,gold,true));
        android.widget.GridLayout chapterGrid=new android.widget.GridLayout(this);
        chapterGrid.setColumnCount(4);
        chapterGrid.setUseDefaultMargins(true);
        TextView[] chapterButtons=new TextView[chapterTexts.size()];
        ScrollView passageScroll=new ScrollView(this);
        TextView passage=text(chapterTexts.get(0),18,ink,false);
        passage.setLineSpacing(5f,1.12f);
        passage.setTextSize(getSharedPreferences("archive_settings",MODE_PRIVATE).getInt("font_size",18));
        enablePassageSelection(passage);
        passageScroll.addView(passage);
        Runnable refreshSelection=()->{
            for(int i=0;i<chapterButtons.length;i++){
                TextView button=chapterButtons[i];
                if(button!=null){
                    button.setTextColor(i==selected[0]?gold:ink);
                    button.setBackground(shape(i==selected[0]?bg:panel));
                }
            }
            passage.setText(chapterTexts.get(selected[0]));
            passageScroll.scrollTo(0,0);
        };
        for(int i=0;i<chapterTexts.size();i++){
            final int index=i;
            TextView button=text(String.valueOf(numbers.get(i)),16,ink,true);
            button.setGravity(Gravity.CENTER);
            button.setPadding(8,12,8,12);
            button.setBackground(shape(panel));
            android.widget.GridLayout.LayoutParams params=new android.widget.GridLayout.LayoutParams();
            params.width=0;
            params.height=-2;
            params.columnSpec=android.widget.GridLayout.spec(i%4,1f);
            params.setMargins(3,3,3,3);
            chapterGrid.addView(button,params);
            chapterButtons[i]=button;
            button.setOnClickListener(v->{selected[0]=index;refreshSelection.run();});
        }
        reader.addView(chapterGrid,new LinearLayout.LayoutParams(-1,-2));
        LinearLayout.LayoutParams passageParams=new LinearLayout.LayoutParams(-1,0,1);
        passageParams.setMargins(0,10,0,0);
        reader.addView(passageScroll,passageParams);
        LinearLayout controls=new LinearLayout(this);
        controls.setGravity(Gravity.CENTER);
        Button previous=new Button(this);
        previous.setText("Previous");
        previous.setOnClickListener(v->{if(selected[0]>0){selected[0]--;refreshSelection.run();}});
        Button next=new Button(this);
        next.setText("Next");
        next.setOnClickListener(v->{if(selected[0]<chapterTexts.size()-1){selected[0]++;refreshSelection.run();}});
        TextView source=text("Text source",13,gold,true);
        source.setGravity(Gravity.CENTER);
        source.setOnClickListener(v->showInfo("John manuscript and translation notes",attribution));
        controls.addView(previous,new LinearLayout.LayoutParams(0,-2,1));
        controls.addView(source,new LinearLayout.LayoutParams(0,-2,1));
        controls.addView(next,new LinearLayout.LayoutParams(0,-2,1));
        reader.addView(controls);
        refreshSelection.run();
        android.app.AlertDialog dialog=new android.app.AlertDialog.Builder(this)
            .setTitle(title+" · Chapter 1 of "+chapterTexts.size())
            .setView(reader)
            .setPositiveButton("Close",null)
            .create();
        dialog.show();
        dialog.getWindow().setLayout(-1,(int)(getResources().getDisplayMetrics().heightPixels*0.88));
    }

    boolean hasUnifiedSourceArchive(String writingId){
        return "john".equals(writingId)||"didache".equals(writingId)||"hermas".equals(writingId)
            ||"barnabas".equals(writingId)||writingId.startsWith("ignatius_")
            ||"gospel_thomas".equals(writingId);
    }

    void openUnifiedSourceArchive(org.json.JSONObject record){
        String writingId=record.optString("id","");
        if("john".equals(writingId)){openJohnWitnessComparison();return;}
        if("didache".equals(writingId)){openDidacheArchive();return;}
        if("hermas".equals(writingId)){openHermasArchive();return;}
        if("barnabas".equals(writingId)){openBarnabasArchive();return;}
        if(writingId.startsWith("ignatius_")){openIgnatiusArchive();return;}
        if("gospel_thomas".equals(writingId)){openThomasArchive();return;}
        showInfo("Source text unavailable","No separately imported original-language archive is connected to this writing yet.");
    }

    void showUnifiedWritingStudy(org.json.JSONObject record){
        StringBuilder detail=new StringBuilder();
        detail.append(record.optString("description","Description not yet available.")).append("\n\n");
        detail.append("Historical setting: ").append(record.optString("historical_anchor","Not established")).append("\n");
        boolean hasDate=!record.isNull("composition_date_start_ce")&&!record.isNull("composition_date_end_ce");
        String date=hasDate?(record.optInt("composition_date_start_ce")==record.optInt("composition_date_end_ce")?record.optInt("composition_date_start_ce")+" CE":record.optInt("composition_date_start_ce")+"–"+record.optInt("composition_date_end_ce")+" CE"):"Undetermined";
        detail.append("Estimated composition: ").append(date).append("\n");
        detail.append("Genre: ").append(record.optString("genre","Not classified")).append("\n");
        detail.append("Attribution and authorship: ").append(record.optString("attribution_status","Not established")).append("\n\n");
        detail.append("Textual and preservation status: ").append(record.optString("textual_status","Not documented")).append("\n");
        detail.append("Preservation category: ").append(record.optString("preservation_status","Not classified")).append("\n");
        detail.append("Collection relationship: ").append(record.optString("scope_relationship","Not classified")).append("\n");
        if(!record.optString("related_scriptural_reference","").isEmpty())detail.append("Related reference: ").append(record.optString("related_scriptural_reference")).append("\n");
        org.json.JSONArray fragments=record.optJSONArray("surviving_fragments");
        if(fragments!=null&&fragments.length()>0){
            detail.append("\nSURVIVING FRAGMENTS AND ANCIENT CITATIONS\n");
            for(int i=0;i<fragments.length();i++){
                org.json.JSONObject fragment=fragments.optJSONObject(i);if(fragment==null)continue;
                detail.append("\n").append(fragment.optString("fragment_id","Fragment")).append("\n");
                for(String key:new String[]{"transmitting_author","source_work","passage","language_of_surviving_source","content_scope","status"}){
                    String value=fragment.optString(key,"");if(!value.isEmpty())detail.append(key.replace("_"," ")).append(": ").append(value).append("\n");
                }
                String fragmentText=fragment.optString("english_paraphrase","");
                if(!fragmentText.isEmpty())detail.append("Study summary (not the text):\n").append(fragmentText).append("\n");
                String fragmentType=fragment.optString("text_type","");if(!fragmentType.isEmpty())detail.append("Text note: ").append(fragmentType).append("\n");
                String fragmentSource=fragment.optString("source_url","");if(!fragmentSource.isEmpty())detail.append("Fragment source: ").append(fragmentSource).append("\n");
            }
        }
        org.json.JSONArray witnesses=record.optJSONArray("manuscript_witnesses");
        if(witnesses!=null&&witnesses.length()>0){
            detail.append("\nMANUSCRIPT AND TRANSMISSION WITNESSES\n");
            for(int i=0;i<witnesses.length();i++){
                org.json.JSONObject w=witnesses.optJSONObject(i);if(w==null)continue;
                detail.append("\n").append(w.optString("siglum",w.optString("id",w.optString("name","Witness")))).append("\n");
                for(String key:new String[]{"shelfmark","writing","material","date","provenance","current_location","contents","text_status","transcription_note","lacuna_policy","rights_note"}){
                    String value=w.optString(key,"");if(!value.isEmpty())detail.append(key.replace("_"," ")).append(": ").append(value).append("\n");
                }
                org.json.JSONArray greek=w.optJSONArray("greek_transcription_lines");if(greek==null)greek=w.optJSONArray("greek_transcription_lines_recto");
                if(greek!=null&&greek.length()>0){detail.append("Greek transcription (as recorded):\n");for(int k=0;k<greek.length();k++)detail.append(greek.optString(k)).append("\n");}
                org.json.JSONArray verso=w.optJSONArray("greek_transcription_lines_verso");
                if(verso!=null&&verso.length()>0){detail.append("Greek transcription, verso:\n");for(int k=0;k<verso.length();k++)detail.append(verso.optString(k)).append("\n");}
                for(String key:new String[]{"english_translation","english_translation_recto","english_translation_verso","translation_note"}){
                    String value=w.optString(key,"");if(!value.isEmpty())detail.append(key.replace("_"," ")+":\n").append(value).append("\n");
                }
                org.json.JSONArray translations=w.optJSONArray("english_translation_lines");
                if(translations!=null&&translations.length()>0){detail.append("English rendering of this witness excerpt:\n");for(int k=0;k<translations.length();k++)detail.append(translations.optString(k)).append("\n");}
                org.json.JSONArray srcs=w.optJSONArray("sources");if(srcs==null)srcs=w.optJSONArray("source_references");
                if(srcs!=null)for(int k=0;k<srcs.length();k++){org.json.JSONObject src=srcs.optJSONObject(k);if(src!=null)detail.append("Source: ").append(src.optString("title","Reference")).append(" ").append(src.optString("url","")).append("\n");}
                String source=w.optString("source","");if(!source.isEmpty())detail.append("Source: ").append(source).append("\n");
            }
        }
        org.json.JSONArray sources=record.optJSONArray("research_sources");
        if(sources!=null&&sources.length()>0){detail.append("\nRESEARCH REFERENCES\n");for(int i=0;i<sources.length();i++){org.json.JSONObject source=sources.optJSONObject(i);if(source!=null)detail.append(source.optString("title","Source")).append("\n").append(source.optString("url","")).append("\n");}}
        TextView view=text(detail.toString(),14,ink,false);enablePassageSelection(view);
        android.text.util.Linkify.addLinks(view,android.text.util.Linkify.WEB_URLS);view.setMovementMethod(android.text.method.LinkMovementMethod.getInstance());
        ScrollView scroll=new ScrollView(this);scroll.setPadding(12,8,12,8);scroll.addView(view);
        android.app.AlertDialog.Builder builder=new android.app.AlertDialog.Builder(this)
            .setTitle(record.optString("title","Writing"))
            .setView(scroll)
            .setPositiveButton("Read complete English text",(dialog,which)->showUnifiedEnglishReading(record))
            .setNegativeButton("Close",null);
        if(hasUnifiedSourceArchive(record.optString("id","")))
            builder.setNeutralButton("Open available source text",(dialog,which)->openUnifiedSourceArchive(record));
        builder.show();
    }

    String libraryCategory="Bookmarks";
    void renderLibrary(){
        if(section.equals("Favorites"))libraryCategory="Bookmarks";
        if(section.equals("Reading History"))libraryCategory="History";
        content.addView(text("Your saved research stays on this device.",13,muted,false));
        LinearLayout tabs=new LinearLayout(this);tabs.setOrientation(LinearLayout.HORIZONTAL);
        String[] categories={"Bookmarks","Highlights","Notes","History"};
        for(String category:categories){
            Button tab=new Button(this);tab.setText(category);tab.setTextSize(11);tab.setTextColor(category.equals(libraryCategory)?gold:ink);tab.setBackground(shape(panel));
            LinearLayout.LayoutParams tp=new LinearLayout.LayoutParams(0,-2,1);tp.setMargins(2,4,2,8);tabs.addView(tab,tp);
            tab.setOnClickListener(v->{libraryCategory=category;renderLibrary();});
        }
        content.addView(tabs);
        android.content.SharedPreferences prefs=getSharedPreferences("archive_library",MODE_PRIVATE);
        ArrayList<String> items=new ArrayList<>();
        String storageKey=libraryCategory.equals("History")?"history":libraryCategory.toLowerCase();
        if(libraryCategory.equals("Notes")){
            for(Map.Entry<String,?> entry:prefs.getAll().entrySet())if(entry.getKey().startsWith("note:")&&entry.getValue() instanceof String&&!((String)entry.getValue()).toString().trim().isEmpty())items.add(entry.getKey().substring(5)+"  "+entry.getValue().toString());
        }else{
            String stored=prefs.getString(storageKey,"");
            if(!stored.isEmpty())items.addAll(Arrays.asList(stored.split("\\n")));
        }
        if(items.isEmpty()){content.addView(text("No "+libraryCategory.toLowerCase()+" saved yet.",14,muted,false));return;}
        for(String item:items){
            if(item.trim().isEmpty())continue;
            String label=item;int split=item.indexOf("  ");if(split>0)label=item.substring(0,split);
            final String rowLabel=label;
            final String rowItem=item;
            final String activeCategory=libraryCategory;
            TextView row=text(rowLabel,15,ink,true);row.setBackground(shape(panel));
            LinearLayout.LayoutParams rp=new LinearLayout.LayoutParams(-1,-2);rp.setMargins(0,4,0,4);content.addView(row,rp);
            row.setOnClickListener(v->{
                if(activeCategory.equals("History")){openBook(rowItem);return;}
                if(activeCategory.equals("Notes")){
                    String key="note:"+rowLabel;EditText editor=new EditText(this);editor.setMinLines(4);editor.setText(prefs.getString(key,""));
                    new android.app.AlertDialog.Builder(this).setTitle("Note · "+rowLabel).setView(editor)
                        .setNegativeButton("Close",null).setNeutralButton("Delete",(d,w)->{prefs.edit().remove(key).apply();renderLibrary();})
                        .setPositiveButton("Save",(d,w)->{prefs.edit().putString(key,editor.getText().toString()).apply();renderLibrary();}).show();
                    return;
                }
                TextView detail=text(rowItem,14,ink,false);ScrollView sv=new ScrollView(this);sv.setPadding(12,8,12,8);sv.addView(detail);
                new android.app.AlertDialog.Builder(this).setTitle(rowLabel).setView(sv)
                    .setNegativeButton("Close",null).setPositiveButton("Remove",(d,w)->{
                        String key=activeCategory.equals("Highlights")?"highlights":"bookmarks";
                        removeLibraryEntry(key,rowItem);renderLibrary();
                    }).show();
            });
        }
    }
    void removeLibraryEntry(String key,String target){
        android.content.SharedPreferences prefs=getSharedPreferences("archive_library",MODE_PRIVATE);
        String stored=prefs.getString(key,"");ArrayList<String> kept=new ArrayList<>();
        for(String line:stored.split("\\n"))if(!line.equals(target)&&!line.trim().isEmpty())kept.add(line);
        prefs.edit().putString(key,android.text.TextUtils.join("\\n",kept)).apply();
    }

    void openAiTranslator(){startActivity(new Intent(this,AiTranslatorActivity.class));}

    String codeFor(String name){
        String[][] pairs={{"Genesis","Gen"},{"Exodus","Exod"},{"Leviticus","Lev"},{"Numbers","Num"},{"Deuteronomy","Deut"},{"Joshua","Josh"},{"Judges","Judg"},{"Ruth","Ruth"},{"1 Samuel","1Sam"},{"2 Samuel","2Sam"},{"1 Kings","1Kgs"},{"2 Kings","2Kgs"},{"1 Chronicles","1Chr"},{"2 Chronicles","2Chr"},{"Ezra","Ezra"},{"Nehemiah","Neh"},{"Esther","Esth"},{"Job","Job"},{"Psalms","Ps"},{"Proverbs","Prov"},{"Ecclesiastes","Eccl"},{"Song of Songs","Song"},{"Isaiah","Isa"},{"Jeremiah","Jer"},{"Lamentations","Lam"},{"Ezekiel","Ezek"},{"Daniel","Dan"},{"Hosea","Hos"},{"Joel","Joel"},{"Amos","Amos"},{"Obadiah","Obad"},{"Jonah","Jonah"},{"Micah","Mic"},{"Nahum","Nah"},{"Habakkuk","Hab"},{"Zephaniah","Zeph"},{"Haggai","Hag"},{"Zechariah","Zech"},{"Malachi","Mal"},{"Matthew","Matt"},{"Mark","Mark"},{"Luke","Luke"},{"John","John"},{"Acts","Acts"},{"Romans","Rom"},{"1 Corinthians","1Cor"},{"2 Corinthians","2Cor"},{"Galatians","Gal"},{"Ephesians","Eph"},{"Philippians","Phil"},{"Colossians","Col"},{"1 Thessalonians","1Thess"},{"2 Thessalonians","2Thess"},{"1 Timothy","1Tim"},{"2 Timothy","2Tim"},{"Titus","Titus"},{"Philemon","Phlm"},{"Hebrews","Heb"},{"James","Jas"},{"1 Peter","1Pet"},{"2 Peter","2Pet"},{"1 John","1John"},{"2 John","2John"},{"3 John","3John"},{"Jude","Jude"},{"Revelation","Rev"}};
        String[][] apocrypha={{"1 Esdras","1 Esdras"},{"Tobit","Tobit"},{"Judith","Judith"},{"Esther (Greek)","Esther (Greek)"},{"Wisdom of Solomon","Wisdom of Solomon"},{"Sirach","Sirach"},{"Baruch","Baruch"},{"Letter of Jeremiah","Letter of Jeremiah"},{"1 Maccabees","1 Maccabees"},{"2 Maccabees","2 Maccabees"},{"3 Maccabees","3 Maccabees"},{"4 Maccabees","4 Maccabees"},{"Susanna (Old Greek)","Susanna (Old Greek)"},{"Susanna (Theodotion)","Susanna (Theodotion)"},{"Daniel (Old Greek)","Daniel (Old Greek)"},{"Daniel (Theodotion)","Daniel (Theodotion)"},{"Bel and the Dragon (Old Greek)","Bel and the Dragon (Old Greek)"},{"Bel and the Dragon (Theodotion)","Bel and the Dragon (Theodotion)"},{"Odes","Odes"},{"Prayer of Manasseh (Greek)","Prayer of Manasseh (Greek)"},{"Psalm 151","Psalm 151"},{"2 Esdras / 4 Ezra (Latin)","2 Esdras / 4 Ezra (Latin)"},{"Prayer of Manasseh (Latin)","Prayer of Manasseh (Latin)"}};
        for(String[] p:apocrypha) if(p[0].equals(name)) return p[1];
        for(String[] p:pairs) if(p[0].equals(name)) return p[1]; return null;
    }
    boolean matchesExact(String text, String needle){
        if(needle==null||needle.length()==0)return false;
        String lower=text.toLowerCase(java.util.Locale.ROOT);
        String term=needle.toLowerCase(java.util.Locale.ROOT);
        int position=0;
        while((position=lower.indexOf(term,position))>=0){
            int end=position+term.length();
            boolean left=position==0||!isWordCharacter(lower.charAt(position-1));
            boolean right=end==lower.length()||!isWordCharacter(lower.charAt(end));
            if(left&&right)return true;
            position++;
        }
        return false;
    }
    boolean isWordCharacter(char value){
        int type=Character.getType(value);
        return Character.isLetterOrDigit(value)||type==Character.NON_SPACING_MARK||
            type==Character.COMBINING_SPACING_MARK||type==Character.ENCLOSING_MARK;
    }


    void searchCorpus(String query){
        final String exact=query;
        new android.os.AsyncTask<Void,Void,ArrayList<String>>(){
            protected ArrayList<String> doInBackground(Void... ignored){
                ArrayList<String> hits=new ArrayList<>();
                String needle=exact.toLowerCase(java.util.Locale.ROOT);
                try{
                    java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("corpus/verses.jsonl"),"UTF-8"));
                    String line;
                    while((line=reader.readLine())!=null && hits.size()<100){
                        org.json.JSONObject obj=new org.json.JSONObject(line);
                        String body=obj.optString("text");
                        String reference=obj.optString("ref");
                        String book=obj.optString("book");
                        String sourceReference=obj.optString("source_reference");
                        if(matchesExact(body,needle)||matchesExact(reference,needle)||matchesExact(book,needle)||matchesExact(sourceReference,needle))
                            hits.add("[Verse corpus] "+(book.length()>0?book+" — ":"")+reference+"  "+body);
                    }
                    reader.close();
                    if(hits.size()<100){
                        java.io.BufferedReader catalogReader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("catalog/dss_passage_concordance.json"),"UTF-8"));
                        StringBuilder raw=new StringBuilder();while((line=catalogReader.readLine())!=null)raw.append(line);catalogReader.close();
                        org.json.JSONArray records=new org.json.JSONObject(raw.toString()).optJSONArray("records");
                        if(records!=null)for(int i=0;i<records.length()&&hits.size()<100;i++){
                            org.json.JSONObject record=records.getJSONObject(i);
                            org.json.JSONArray lines=record.optJSONArray("transcription_line_map");
                            if(lines!=null)for(int k=0;k<lines.length()&&hits.size()<100;k++){
                                org.json.JSONObject entry=lines.getJSONObject(k);
                                String body=entry.optString("transcription_text");
                                String group=entry.optString("group");
                                String sourceReference=entry.optString("source_reference");
                                String passageRefs=entry.optJSONArray("passages")==null?"":entry.optJSONArray("passages").toString();
                                if(matchesExact(body,needle)||matchesExact(group,needle)||matchesExact(sourceReference,needle)||matchesExact(passageRefs,needle)){
                                    hits.add("[DSS "+record.optString("manuscript_id")+"] "+group+" line "+entry.optInt("digital_line")+"  "+body);
                                }
                            }
                            org.json.JSONArray additionalSources=record.optJSONArray("additional_transcription_sources");
                            if(additionalSources!=null)for(int sourceIndex=0;sourceIndex<additionalSources.length()&&hits.size()<100;sourceIndex++){
                                org.json.JSONObject source=additionalSources.getJSONObject(sourceIndex);
                                org.json.JSONArray sourceSections=source.optJSONArray("sections");
                                if(sourceSections==null)continue;
                                for(int sectionIndex=0;sectionIndex<sourceSections.length()&&hits.size()<100;sectionIndex++){
                                    org.json.JSONObject section=sourceSections.getJSONObject(sectionIndex);
                                    String body=section.optString("pdf_text_lines");
                                    String group=section.optString("fragment_group");
                                    String sourceTitle=source.optString("title");
                                    String passageRefs=section.optJSONArray("passage_refs")==null?"":section.optJSONArray("passage_refs").toString();
                                    if(matchesExact(body,needle)||matchesExact(group,needle)||matchesExact(sourceTitle,needle)||matchesExact(passageRefs,needle)){
                                        hits.add("[DSS "+record.optString("manuscript_id")+" — "+sourceTitle+"] "+group+"  "+body);
                                    }
                                }
                            }
                        }
                    }
                }catch(Exception e){hits.add("Search data unavailable: "+e.getMessage());}
                if(hits.size()<100){
                    try{
                        java.io.BufferedReader dssReader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("dss/etcbc_transcriptions.jsonl"),"UTF-8"),65536);
                        String dssLine;
                        while((dssLine=dssReader.readLine())!=null&&hits.size()<100){
                            org.json.JSONObject record=new org.json.JSONObject(dssLine);
                            String body=record.optString("transcription_text");
                            String normalized=record.optString("normalized_text");
                            String coordinate=record.optString("scroll")+" "+record.optString("fragment")+" line "+record.optString("line");
                            String parallels=record.optJSONArray("parallel_references")==null?"":record.optJSONArray("parallel_references").toString();
                            if(matchesExact(body,needle)||matchesExact(normalized,needle)||matchesExact(coordinate,needle)||matchesExact(parallels,needle))
                                hits.add("[ETCBC / Abegg DSS] "+coordinate+"  "+body);
                        }
                        dssReader.close();
                    }catch(Exception dssError){hits.add("ETCBC DSS search unavailable: "+dssError.getMessage());}
                }
                return hits;
            }
            protected void onPostExecute(ArrayList<String> hits){
                if(hits.isEmpty()){
                    new android.app.AlertDialog.Builder(MainActivity.this).setTitle("No exact text matches").setMessage("No occurrence of ["+exact+"] was found in the imported verse corpus or indexed DSS transcriptions.").setPositiveButton("Close",null).show();
                    return;
                }
                StringBuilder result=new StringBuilder();
                for(String hit:hits)result.append(hit).append("\n\n");
                if(hits.size()==100)result.append("Results capped at 100. Refine the phrase to narrow the search.");
                TextView view=text(result.toString(),14,ink,false);enablePassageSelection(view);
                ScrollView sv=new ScrollView(MainActivity.this);sv.setPadding(14,8,14,8);sv.addView(view);
                new android.app.AlertDialog.Builder(MainActivity.this).setTitle("Exact text search: "+exact).setView(sv).setNegativeButton("Back to "+returnSection,(d,w)->{navigateTo(returnSection);}).setNeutralButton("Home",(d,w)->{previousSection="Home";section="Home";show();}).setPositiveButton("Close",null).show();
            }
        }.executeOnExecutor(android.os.AsyncTask.THREAD_POOL_EXECUTOR);
    }

    void openBook(String name){
        android.content.SharedPreferences library=getSharedPreferences("archive_library",MODE_PRIVATE);String history=library.getString("history","");String updated=history.isEmpty()?name:(name.equals(history.split("\n",2)[0])?history:name+"\n"+history);library.edit().putString("last_book",name).putString("history",updated).apply();
        final String bookName=name;
        final String code=codeFor(bookName);
        if(code==null){new android.app.AlertDialog.Builder(this).setMessage("No text mapping is registered for "+bookName+".").setPositiveButton("Close",null).show();return;}
        final boolean useDssReconstruction=java.util.Arrays.asList("Gen","Exod","Lev","Num","Deut","Josh","Judg","Ruth","1Sam","2Sam","1Kgs","2Kgs","1Chr","2Chr","Ezra","Neh","Esth","Job","Ps","Prov","Eccl","Song","Isa","Jer","Lam","Ezek","Dan","Hos","Joel","Amos","Obad","Jonah","Mic","Nah","Hab","Zeph","Hag","Zech","Mal").contains(code);
        final String corpusAsset=useDssReconstruction?"corpus/reconstructed_verses.jsonl":"corpus/verses.jsonl";
        new android.os.AsyncTask<Void,Void,org.json.JSONObject>(){
            protected org.json.JSONObject doInBackground(Void... ignored){
                org.json.JSONObject result=new org.json.JSONObject();
                org.json.JSONArray verses=new org.json.JSONArray();
                StringBuilder metadata=new StringBuilder();
                int scanned=0;
                try{
                    java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open(corpusAsset),"UTF-8"),65536);
                    String line;
                    while((line=reader.readLine())!=null){
                        scanned++;
                        org.json.JSONObject obj=new org.json.JSONObject(line);
                        String ref=obj.optString("ref");
                        String recordBook=obj.optString("book");
                        String recordCode=obj.optString("book_code");
                        boolean match=bookName.equals(recordBook)||bookName.equals(recordCode)||
                            code.equals(recordCode)||ref.startsWith(code+".")||ref.startsWith(code+" ")||
                            ref.startsWith(bookName+" ")||ref.startsWith(bookName+":");
                        if(!match)continue;
                        if(verses.length()==0){
                            metadata.append("Source: ").append(obj.optString("source")).append("\n");
                            metadata.append("Edition: ").append(obj.optString("edition")).append("\n");
                            metadata.append("Witness basis: ").append(obj.optString("witness_basis")).append("\n");
                            metadata.append("Text type: ").append(obj.optString("transcription_type")).append("\n");
                            metadata.append("Licence: ").append(obj.optString("license",obj.optString("text_status"))).append("\n");
                            metadata.append("Attribution: ").append(obj.optString("attribution")).append("\n");
                            metadata.append("Source URL: ").append(obj.optString("source_url")).append("\n\n");
                        }
                        String displayRef=ref;
                        if(ref.startsWith(code+"."))displayRef=ref.substring(code.length()+1).replace('.',':');
                        else if(ref.startsWith(code+" "))displayRef=ref.substring(code.length()).trim();
                        else if(ref.startsWith(bookName+" "))displayRef=ref.substring(bookName.length()).trim();
                        org.json.JSONObject verse=new org.json.JSONObject();
                        verse.put("reference",displayRef);
                        verse.put("text",obj.optString("text"));
                        verse.put("language",obj.optString("language"));
                        if(obj.has("reconstruction_note"))verse.put("reconstruction_note",obj.optString("reconstruction_note"));
                        verses.put(verse);
                    }
                    reader.close();
                    result.put("metadata",metadata.toString());
                    result.put("verses",verses);
                    result.put("scanned",scanned);
                    result.put("book",bookName);
                    return result;
                }catch(Exception e){
                    try{result.put("error",e.getClass().getSimpleName()+": "+e.getMessage());result.put("scanned",scanned);result.put("verses",verses);}catch(Exception ignoredError){}
                    return result;
                }
            }
            protected void onPostExecute(org.json.JSONObject result){
                if(result==null){
                    new android.app.AlertDialog.Builder(MainActivity.this).setTitle(bookName).setMessage("The bundled corpus could not be opened.").setPositiveButton("Close",null).show();return;
                }
                org.json.JSONArray verses=result.optJSONArray("verses");
                int count=verses==null?0:verses.length();
                if(count==0){
                    String detail=result.optString("error","No matching records. Scanned "+result.optInt("scanned")+" bundled lines. Book code: "+code);
                    new android.app.AlertDialog.Builder(MainActivity.this).setTitle(bookName+" — no verses loaded").setMessage(detail).setPositiveButton("Close",null).show();return;
                }
                android.content.SharedPreferences readingPrefs=getSharedPreferences("archive_library",MODE_PRIVATE);
                java.util.LinkedHashSet<String> chapterSet=new java.util.LinkedHashSet<>();
                for(int i=0;i<count;i++){org.json.JSONObject verse=verses.optJSONObject(i);if(verse==null)continue;String ref=verse.optString("reference");String chapter=ref.contains(":")?ref.substring(0,ref.indexOf(':')):"1";chapterSet.add(chapter);}
                ArrayList<String> chapters=new ArrayList<>(chapterSet);
                if(chapters.isEmpty())chapters.add("1");
                String savedChapter=readingPrefs.getString("last_chapter:"+bookName,chapters.get(0));
                int initialChapter=Math.max(0,chapters.indexOf(savedChapter));
                LinearLayout reader=new LinearLayout(MainActivity.this);reader.setOrientation(1);reader.setPadding(12,8,12,8);
                reader.addView(text(count+" verses loaded from the offline corpus",13,gold,true));
                TextView meta=text(result.optString("metadata"),12,muted,false);
                meta.setAutoLinkMask(android.text.util.Linkify.WEB_URLS);
                meta.setMovementMethod(android.text.method.LinkMovementMethod.getInstance());
                reader.addView(meta);
                reader.addView(text(useDssReconstruction?"Reconstructed Hebrew reading, verse by verse. DSS words replace WLC words only when their ordered alignment meets the 70% threshold; the WLC supplies remaining word positions. Each verse identifies whether it is hybrid, fragment-only, or WLC-only. Long-press to select and Copy.":"Original-language text only. Long-press to select and Copy. The source edition and witness basis are identified above.",12,muted,false));
                if("DSS Hebrew Archive".equals(section)){
                    Button dssEvidence=new Button(MainActivity.this);dssEvidence.setText("View surviving DSS manuscript lines");
                    dssEvidence.setOnClickListener(v->openDssBookEntry(bookName));
                    reader.addView(dssEvidence);
                }
                LinearLayout chapterBar=new LinearLayout(MainActivity.this);chapterBar.setGravity(Gravity.CENTER_VERTICAL);
                Button previous=new Button(MainActivity.this);previous.setText("‹ Previous");
                Spinner chapterPicker=new Spinner(MainActivity.this);
                ArrayAdapter<String> chapterAdapter=new ArrayAdapter<>(MainActivity.this,android.R.layout.simple_spinner_item,chapters);
                chapterAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);chapterPicker.setAdapter(chapterAdapter);
                if(java.util.Arrays.asList("Gen","Exod","Lev","Num","Deut").contains(code)){
                    Button samaritanWitness=new Button(MainActivity.this);
                    samaritanWitness.setText("Compare Samaritan Pentateuch witness");
                    samaritanWitness.setOnClickListener(v->openSamaritanChapterWitness(code,chapters.get(Math.max(0,chapterPicker.getSelectedItemPosition()))));
                    reader.addView(samaritanWitness);
                }
                Button next=new Button(MainActivity.this);next.setText("Next ›");
                chapterBar.addView(previous,new LinearLayout.LayoutParams(0,-2,1));
                chapterBar.addView(chapterPicker,new LinearLayout.LayoutParams(0,-2,1));
                chapterBar.addView(next,new LinearLayout.LayoutParams(0,-2,1));
                reader.addView(chapterBar);
                ScrollView sv=new ScrollView(MainActivity.this);sv.setFillViewport(true);sv.setPadding(8,8,8,8);
                LinearLayout chapterContent=new LinearLayout(MainActivity.this);chapterContent.setOrientation(1);sv.addView(chapterContent);
                reader.addView(sv,new LinearLayout.LayoutParams(-1,0,1));
                final boolean[] pickerReady={false};
                Runnable renderChapter=()->{
                    int selected=Math.max(0,chapterPicker.getSelectedItemPosition());
                    String selectedChapter=chapters.get(selected);
                    readingPrefs.edit().putString("last_book",bookName).putString("last_chapter:"+bookName,selectedChapter).apply();
                    chapterContent.removeAllViews();
                    chapterContent.addView(text(bookName+" — Chapter "+selectedChapter,19,gold,true));
                    int readingSize=getSharedPreferences("archive_settings",MODE_PRIVATE).getInt("font_size",16);
                    for(int i=0;i<count;i++){
                        org.json.JSONObject verse=verses.optJSONObject(i);if(verse==null)continue;
                        String reference=verse.optString("reference"),body=verse.optString("text"),language=verse.optString("language");
                        String verseChapter=reference.contains(":")?reference.substring(0,reference.indexOf(':')):"1";
                        if(!selectedChapter.equals(verseChapter))continue;
                        LinearLayout passageCard=new LinearLayout(MainActivity.this);passageCard.setOrientation(1);passageCard.setPadding(10,6,10,6);passageCard.setBackground(shape(panel));
                        TextView row=text(reference+"\\n"+body,readingSize,ink,false);row.setTag(reference);enablePassageSelection(row);
                        LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,-2);p.setMargins(0,4,0,4);passageCard.addView(row,p);
                        String reconstructionNote=verse.optString("reconstruction_note","");
                        if(!reconstructionNote.isEmpty()){TextView sourceNote=text(reconstructionNote,11,muted,false);sourceNote.setPadding(14,0,14,7);passageCard.addView(sourceNote);}
                        TextView tools=text("Passage tools  ·  Tap to translate with Gemini AI",12,gold,true);tools.setOnClickListener(v->showPassageActions(reference,body,language));passageCard.addView(tools);
                        passageCard.setOnClickListener(v->openAiTranslator(reference,body,language));chapterContent.addView(passageCard);
                    }
                    previous.setEnabled(selected>0);next.setEnabled(selected<chapters.size()-1);
                };
                chapterPicker.setOnItemSelectedListener(new android.widget.AdapterView.OnItemSelectedListener(){
                    public void onItemSelected(android.widget.AdapterView<?> parent,View view,int position,long id){if(pickerReady[0])renderChapter.run();}
                    public void onNothingSelected(android.widget.AdapterView<?> parent){}
                });
                previous.setOnClickListener(v->{int p=chapterPicker.getSelectedItemPosition();if(p>0)chapterPicker.setSelection(p-1);});
                next.setOnClickListener(v->{int p=chapterPicker.getSelectedItemPosition();if(p<chapters.size()-1)chapterPicker.setSelection(p+1);});
                chapterPicker.setSelection(initialChapter);pickerReady[0]=true;renderChapter.run();
                new android.app.AlertDialog.Builder(MainActivity.this).setTitle(bookName+" — "+count+" verses").setView(reader).setNegativeButton("Back to "+returnSection,(d,w)->{navigateTo(returnSection);}).setNeutralButton("Home",(d,w)->{previousSection="Home";section="Home";show();}).setPositiveButton("Close",null).show();
            }
        }.executeOnExecutor(android.os.AsyncTask.THREAD_POOL_EXECUTOR);
    }

    private void appendLibraryEntry(String key,String entry){android.content.SharedPreferences p=getSharedPreferences("archive_library",MODE_PRIVATE);String old=p.getString(key,"");for(String line:old.split("\n"))if(line.equals(entry))return;p.edit().putString(key,entry+(old.isEmpty()?"":"\n"+old)).apply();}
    private void showPassageActions(String reference,String body,String sourceLanguage){String[] actions={"AI translate / analyze","Bookmark passage","Highlight passage","Add or edit personal note","Copy full passage","Paste clipboard text into translator","Share passage"};new android.app.AlertDialog.Builder(this).setTitle(reference).setItems(actions,(d,w)->{if(w==0){openAiTranslator(reference,body,sourceLanguage);}else if(w==1){appendLibraryEntry("bookmarks",reference+"  "+body);showInfo("Bookmark saved",reference+" was saved to your personal library.");}else if(w==2){appendLibraryEntry("highlights",reference+"  "+body);showInfo("Highlight saved",reference+" was added to your highlights.");}else if(w==3){android.content.SharedPreferences p=getSharedPreferences("archive_library",MODE_PRIVATE);EditText note=new EditText(this);note.setMinLines(3);note.setText(p.getString("note:"+reference,""));new android.app.AlertDialog.Builder(this).setTitle("Personal note · "+reference).setView(note).setNegativeButton("Cancel",null).setPositiveButton("Save",(a,b)->p.edit().putString("note:"+reference,note.getText().toString()).apply()).show();}else if(w==4){((android.content.ClipboardManager)getSystemService(CLIPBOARD_SERVICE)).setPrimaryClip(android.content.ClipData.newPlainText(reference,reference+" "+body));showInfo("Copied",reference+" copied to clipboard.");}else if(w==5){android.content.ClipboardManager clipboard=(android.content.ClipboardManager)getSystemService(CLIPBOARD_SERVICE);if(clipboard==null||!clipboard.hasPrimaryClip()||clipboard.getPrimaryClip().getItemCount()==0){showInfo("Clipboard empty","Copy text first, then choose Paste.");return;}CharSequence pasted=clipboard.getPrimaryClip().getItemAt(0).coerceToText(this);if(pasted==null||pasted.toString().trim().isEmpty()){showInfo("Clipboard empty","There is no text to paste.");return;}openAiTranslator(reference,pasted.toString(),sourceLanguage);}else{android.content.Intent intent=new android.content.Intent(Intent.ACTION_SEND);intent.setType("text/plain");intent.putExtra(Intent.EXTRA_TEXT,reference+"\\n"+body);startActivity(Intent.createChooser(intent,"Share passage"));}}).show();}
    void openAiTranslator(String reference,String sourceText,String sourceLanguage){Intent intent=new Intent(this,AiTranslatorActivity.class);intent.putExtra("passage_reference",reference);intent.putExtra("passage_text",sourceText);intent.putExtra("source_language",sourceLanguage);intent.putExtra("preferred_target_language",targetLanguageName());startActivity(intent);}

    void renderDssHebrewArchive(String query){
        content.addView(text("ONE ARCHIVE · ORIGINAL-LANGUAGE READINGS AND DSS WITNESSES",12,gold,true));
        content.addView(text("This section now lists only writings with evidence in the imported Dead Sea Scrolls transcriptions. Hebrew Scripture titles appear only when an actual imported DSS line has a mapped parallel reference. Additional writings appear only when an identified Qumran witness is present. Open a book to read the reconstructed text separately, then use the DSS-lines control to inspect the surviving manuscript lines.",13,muted,false));
        content.addView(text("Source: ETCBC / CACCHT Dead Sea Scrolls corpus, Martin G. Abegg transcriptions distributed through Qumran Digital Reader. CC BY-NC 4.0 — non-commercial use only.",12,muted,false));
        renderDssEvidenceIndex(query);
        content.addView(text("The DSS lines are the primary archive evidence. Missing portions are reconstructed only in a separate reading layer from a named, reliable witness; supplied wording is never labelled as DSS. If no reliable witness preserves a missing passage, the gap remains identified rather than invented.",12,gold,false));
    }

    void renderDssEvidenceIndex(String query){
        try{
            java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("dss/dss_book_index.json"),"UTF-8"));
            StringBuilder raw=new StringBuilder();String line;while((line=reader.readLine())!=null)raw.append(line);reader.close();
            org.json.JSONObject index=new org.json.JSONObject(raw.toString());
            content.addView(text("HEBREW SCRIPTURE BOOKS WITH DSS EVIDENCE",12,gold,true));
            org.json.JSONArray books=index.optJSONArray("books");
            int shown=0;
            if(books!=null)for(int i=0;i<books.length();i++){
                org.json.JSONObject book=books.getJSONObject(i);String title=book.optString("title");
                if(!query.isEmpty()&&!title.toLowerCase(java.util.Locale.ROOT).contains(query.toLowerCase(java.util.Locale.ROOT)))continue;
                String label=title+"  ·  "+book.optInt("preserved_line_count")+" DSS lines · "+book.optInt("witness_count")+" witnesses";
                TextView row=text(label+"   ›",15,ink,true);row.setPadding(13,12,13,12);row.setBackground(shape(panel));
                LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,-2);p.setMargins(0,3,0,3);content.addView(row,p);
                row.setOnClickListener(v->openDssArchiveBook(title));shown++;
            }
            content.addView(text("ADDITIONAL WRITINGS PRESERVED IN DSS",12,gold,true));
            org.json.JSONArray related=index.optJSONArray("related_writings");
            if(related!=null)for(int i=0;i<related.length();i++){
                org.json.JSONObject work=related.getJSONObject(i);String title=work.optString("title");
                if(!query.isEmpty()&&!title.toLowerCase(java.util.Locale.ROOT).contains(query.toLowerCase(java.util.Locale.ROOT)))continue;
                String label=title+"  ·  "+work.optInt("preserved_line_count")+" preserved lines";
                TextView row=text(label+"   ›",15,ink,true);row.setPadding(13,12,13,12);row.setBackground(shape(panel));
                LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,-2);p.setMargins(0,3,0,3);content.addView(row,p);
                row.setOnClickListener(v->openDssArchiveBook(title));shown++;
            }
            content.addView(text("Separate manuscript archive: "+index.optInt("scroll_identifier_count")+" scroll identifiers and "+index.optInt("total_line_records")+" imported line records. Open DSS Transcription Archive to inspect every imported scroll, including non-scriptural compositions.",12,muted,false));
            if(shown==0)content.addView(text("No DSS-attested book matches this search.",14,muted,false));
        }catch(Exception e){
            content.addView(text("The DSS book index is unavailable in this build. "+e.getMessage(),13,muted,false));
        }
    }

    ArrayList<String> readDssLostBookTitles(){
        ArrayList<String> titles=new ArrayList<>();
        try{
            java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("catalog/lost_and_referenced_books_catalog.json"),"UTF-8"));
            StringBuilder raw=new StringBuilder();String line;while((line=reader.readLine())!=null)raw.append(line);reader.close();
            org.json.JSONArray records=new org.json.JSONObject(raw.toString()).getJSONArray("records");
            for(int i=0;i<records.length();i++){String title=records.getJSONObject(i).optString("title","");if(!title.isEmpty())titles.add(title);}
        }catch(Exception e){if(entries.get("Lost and Referenced Books")!=null)titles.addAll(entries.get("Lost and Referenced Books"));}
        return titles;
    }

    void openDssArchiveBook(String title){
        String code=codeFor(title);
        if(code!=null){
            openBook(title);
            return;
        }
        if("1 Enoch".equalsIgnoreCase(title)||"Jubilees".equalsIgnoreCase(title)
                ||"Tobit".equalsIgnoreCase(title)||"Sirach".equalsIgnoreCase(title)){
            openDssBookEntry(title);
            return;
        }
        if("Book of Giants".equalsIgnoreCase(title)){
            openBookOfGiantsFragments();
            return;
        }
        if("Book of Noah".equalsIgnoreCase(title)){
            openReferencedBookEntry("Book of Noah (Jubilees reference)");
            return;
        }
        if("Genesis Apocryphon".equalsIgnoreCase(title)||"Prayer of Nabonidus".equalsIgnoreCase(title)){
            openDssBookEntry(title);
            return;
        }
        openReferencedBookEntry(title);
    }

    void renderDssArchiveGroup(String heading,ArrayList<String> titles,String query){
        if(titles==null||titles.isEmpty())return;
        content.addView(text(heading,12,gold,true));
        for(String title:titles){
            if(!query.isEmpty()&&!title.toLowerCase(java.util.Locale.ROOT).contains(query.toLowerCase(java.util.Locale.ROOT)))continue;
            TextView row=text(title+"   ›",15,ink,true);row.setPadding(13,12,13,12);row.setBackground(shape(panel));
            LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,-2);p.setMargins(0,3,0,3);content.addView(row,p);
            row.setOnClickListener(v->openDssArchiveBook(title));
        }
    }

    String[] dssReferenceAliases(String title){
        String t=title.toLowerCase(java.util.Locale.ROOT);
        if(t.equals("genesis"))return new String[]{"genesis","gen."};
        if(t.equals("exodus"))return new String[]{"exodus","exod","ex."};
        if(t.equals("leviticus"))return new String[]{"leviticus","lev."};
        if(t.equals("numbers"))return new String[]{"numbers","num."};
        if(t.equals("deuteronomy"))return new String[]{"deuteronomy","deut","deu."};
        if(t.equals("joshua"))return new String[]{"joshua","josh."};
        if(t.equals("judges"))return new String[]{"judges","judg."};
        if(t.equals("ruth"))return new String[]{"ruth","ruth."};
        if(t.equals("1 samuel"))return new String[]{"1 samuel","1sam","1 sam."};
        if(t.equals("2 samuel"))return new String[]{"2 samuel","2sam","2 sam."};
        if(t.equals("1 kings"))return new String[]{"1 kings","1kgs","1 kgs"};
        if(t.equals("2 kings"))return new String[]{"2 kings","2kgs","2 kgs"};
        if(t.equals("1 chronicles"))return new String[]{"1 chronicles","1chr","1 chr"};
        if(t.equals("2 chronicles"))return new String[]{"2 chronicles","2chr","2 chr"};
        if(t.equals("ezra"))return new String[]{"ezra","ezr."};
        if(t.equals("nehemiah"))return new String[]{"nehemiah","neh."};
        if(t.equals("esther"))return new String[]{"esther","esth."};
        if(t.equals("job"))return new String[]{"job","job."};
        if(t.equals("psalms"))return new String[]{"psalms","psalm","ps."};
        if(t.equals("proverbs"))return new String[]{"proverbs","prov."};
        if(t.equals("ecclesiastes"))return new String[]{"ecclesiastes","eccl."};
        if(t.equals("song of songs"))return new String[]{"song of songs","song","canticles"};
        if(t.equals("isaiah"))return new String[]{"isaiah","isa."};
        if(t.equals("jeremiah"))return new String[]{"jeremiah","jer."};
        if(t.equals("lamentations"))return new String[]{"lamentations","lam."};
        if(t.equals("ezekiel"))return new String[]{"ezekiel","ezek."};
        if(t.equals("daniel"))return new String[]{"daniel","dan."};
        if(t.equals("hosea"))return new String[]{"hosea","hos."};
        if(t.equals("joel"))return new String[]{"joel","joel."};
        if(t.equals("amos"))return new String[]{"amos","amos."};
        if(t.equals("obadiah"))return new String[]{"obadiah","obad."};
        if(t.equals("jonah"))return new String[]{"jonah","jon."};
        if(t.equals("micah"))return new String[]{"micah","mic."};
        if(t.equals("nahum"))return new String[]{"nahum","nah."};
        if(t.equals("habakkuk"))return new String[]{"habakkuk","hab."};
        if(t.equals("zephaniah"))return new String[]{"zephaniah","zeph."};
        if(t.equals("haggai"))return new String[]{"haggai","hag."};
        if(t.equals("zechariah"))return new String[]{"zechariah","zech."};
        if(t.equals("malachi"))return new String[]{"malachi","mal."};
        if(t.contains("tobit"))return new String[]{"tobit","tob."};
        if(t.contains("judith"))return new String[]{"judith","jdt."};
        if(t.contains("sirach"))return new String[]{"sirach","ecclesiasticus","sir."};
        if(t.contains("baruch"))return new String[]{"baruch","bar."};
        if(t.contains("letter of jeremiah"))return new String[]{"letter of jeremiah","epistle of jeremiah"};
        if(t.contains("1 enoch")||t.equals("enoch"))return new String[]{"1 enoch","enoch"};
        if(t.contains("jubilees"))return new String[]{"jubilees","jub."};
        if(t.contains("psalm 151"))return new String[]{"psalm 151","ps 151"};
        return new String[]{t};
    }

    boolean dssScrollMatchesTitle(String title,String scroll){
        String t=title.toLowerCase(java.util.Locale.ROOT);String id=scroll.toLowerCase(java.util.Locale.ROOT).replaceAll("[^a-z0-9]","");
        String[] ids=new String[0];
        if(t.contains("1 enoch")||t.equals("enoch"))ids=new String[]{"4q201","4q202","4q204","4q205","4q206","4q207","4q208","4q209","4q210","4q211","4q212"};
        else if(t.contains("jubilees"))ids=new String[]{"1q17","1q18","2q19","3q5","4q216","4q217","4q218","4q219","4q220","4q221","4q222","4q223","4q224"};
        else if(t.contains("book of giants"))ids=new String[]{"1q23","2q26","4q203","4q530","4q531","4q532","4q533","6q8"};
        else if(t.contains("tobit"))ids=new String[]{"4q196","4q197","4q198","4q199","4q200"};
        else if(t.contains("sirach"))ids=new String[]{"2q18","11q5"};
        else if(t.contains("genesis apocryphon"))ids=new String[]{"1q20"};
        else if(t.contains("prayer of nabonidus"))ids=new String[]{"4q242"};
        for(String witness:ids)if(id.contains(witness))return true;
        return false;
    }

    void openSamaritanChapterWitness(String bookCode,String chapter){
        final String code=bookCode, selectedChapter=chapter;
        new android.os.AsyncTask<Void,Void,String>(){
            protected String doInBackground(Void... ignored){
                StringBuilder out=new StringBuilder();
                try{
                    java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("corpus/samaritan_pentateuch.jsonl"),"UTF-8"),65536);
                    String line;int count=0;
                    while((line=reader.readLine())!=null){
                        org.json.JSONObject row=new org.json.JSONObject(line);
                        if(!code.equals(row.optString("book_code")))continue;
                        String ref=row.optString("ref");
                        String prefix=code+" "+selectedChapter+":";
                        if(!ref.startsWith(prefix))continue;
                        out.append(ref.substring(code.length()).trim()).append("\\n");
                        out.append(row.optString("text")).append("\\n\\n");
                        count++;
                    }
                    reader.close();
                    if(count==0)return "No imported Samaritan Pentateuch verse records were found for this chapter.";
                    return "CACCHT Samaritan Pentateuch · Text-Fabric dataset v7.4.1\\n"+
                        "Witness basis: MS Dublin Chester Beatty Library 751 (Genesis 1:1–Deuteronomy 32:36) and MS Garizim 1 (Deuteronomy 32:36b–34:10).\\n"+
                        "CC BY-NC 4.0 · Separate Samaritan Hebrew scholarly transliteration (g_cons_raw).\\n"+
                        "This is not a DSS reading or WLC text. Transliteration is retained as supplied; it is not converted into Hebrew characters.\\n\\n"+out.toString();
                }catch(Exception e){return "Samaritan witness data unavailable: "+e.getMessage();}
            }
            protected void onPostExecute(String body){
                TextView contentView=text(body,15,ink,false);
                contentView.setTextIsSelectable(true);
                android.widget.ScrollView scroll=new android.widget.ScrollView(MainActivity.this);
                scroll.setPadding(18,12,18,12);scroll.addView(contentView);
                new android.app.AlertDialog.Builder(MainActivity.this)
                    .setTitle("Samaritan Pentateuch — "+code+" "+selectedChapter)
                    .setView(scroll).setPositiveButton("Close",null).show();
            }
        }.execute();
    }

    void openDssBookEntry(String bookTitle){
        final String title=bookTitle;
        final String[] aliases=dssReferenceAliases(title);
        new android.os.AsyncTask<Void,Void,String>(){
            protected String doInBackground(Void... ignored){
                StringBuilder out=new StringBuilder();int count=0;java.util.LinkedHashSet<String> witnesses=new java.util.LinkedHashSet<>();
                try{
                    java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("dss/etcbc_transcriptions.jsonl"),"UTF-8"),65536);
                    String raw;
                    while((raw=reader.readLine())!=null){
                        org.json.JSONObject record=new org.json.JSONObject(raw);
                        String scroll=record.optString("scroll");String refs="";
                        org.json.JSONArray parallel=record.optJSONArray("parallel_references");
                        if(parallel!=null)for(int i=0;i<parallel.length();i++){if(i>0)refs+="; ";refs+=parallel.optString(i);}
                        boolean match=dssScrollMatchesTitle(title,scroll);
                        for(String alias:aliases){if(!match&&!alias.isEmpty()&&(refs.toLowerCase(java.util.Locale.ROOT).contains(alias.toLowerCase(java.util.Locale.ROOT)))){match=true;break;}}
                        if(!match)continue;
                        if(count==0){
                            out.append("DSS transcription source: Martin G. Abegg Jr. / ETCBC-CACCHT, distributed through Qumran Digital Reader.\n");
                            out.append("License: CC BY-NC 4.0 — non-commercial use only.\n");
                            out.append("This view contains only matching manuscript line records. Parallel references are indexing aids, not reconstructed Scripture text.\n\n");
                        }
                        witnesses.add(scroll);
                        out.append(scroll).append(" · Fragment ").append(record.optString("fragment")).append(" · Line ").append(record.optString("line")).append("\n");
                        out.append(record.optString("transcription_text")).append("\n");
                        String normalized=record.optString("normalized_text");
                        if(!normalized.isEmpty()&&!normalized.equals(record.optString("transcription_text")))out.append("Normalized tokens: ").append(normalized).append("\n");
                        if(!refs.isEmpty())out.append("Parallel reference: ").append(refs).append("\n");
                        out.append("\n");count++;
                    }
                    reader.close();
                }catch(Exception e){return "The bundled DSS transcription could not be read: "+e.getMessage();}
                if(count==0)return "No matching line-level record for "+title+" was found in the currently bundled ETCBC/Abegg DSS dataset. This does not prove that no DSS fragment exists; it means this import has no line record mapped to the title. No later manuscript or edition has been used to fill the gap.\n\nArchive index entry: "+title;
                return count+" preserved DSS line records from "+witnesses.size()+" witness identifiers.\n\n"+out.toString();
            }
            protected void onPostExecute(String result){
                TextView view=text(result,15,ink,false);enablePassageSelection(view);
                ScrollView sv=new ScrollView(MainActivity.this);sv.setPadding(12,8,12,8);sv.addView(view);
                android.app.AlertDialog.Builder builder=new android.app.AlertDialog.Builder(MainActivity.this).setTitle(title+" · DSS witness text").setView(sv).setNegativeButton("Back to archive",(d,w)->navigateTo("DSS Hebrew Archive")).setPositiveButton("Close",null);
                if("1 Enoch".equalsIgnoreCase(title))builder.setNeutralButton("Other text witnesses",(d,w)->openEnochWitnessMenu());
                if("Jubilees".equalsIgnoreCase(title))builder.setNeutralButton("Ge'ez editions",(d,w)->openJubileesGeezArchive());
                builder.show();
            }
        }.executeOnExecutor(android.os.AsyncTask.THREAD_POOL_EXECUTOR);
    }

    void renderEtcbcDssIndex(String query){
        try{
            java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("dss/etcbc_scroll_index.json"),"UTF-8"));
            StringBuilder raw=new StringBuilder();String line;while((line=reader.readLine())!=null)raw.append(line);reader.close();
            org.json.JSONObject index=new org.json.JSONObject(raw.toString());
            org.json.JSONArray scrolls=index.getJSONArray("scrolls");
            content.addView(text(index.optInt("total_line_records")+" manuscript lines · "+scrolls.length()+" scroll identifiers",13,gold,true));
            content.addView(text("Source: Martin G. Abegg Jr. transcriptions, ETCBC/CACCHT structured export. CC BY-NC 4.0; non-commercial use only.",12,muted,false));
            content.addView(text("Each entry retains its scroll, fragment and source line label. Transcription display and normalized text are shown separately; parallel references are not merged into the manuscript text.",12,muted,false));
            int shown=0;
            for(int i=0;i<scrolls.length();i++){
                org.json.JSONObject entry=scrolls.getJSONObject(i);
                String scroll=entry.optString("scroll");
                if(!query.isEmpty()&&!scroll.toLowerCase(java.util.Locale.ROOT).contains(query.toLowerCase(java.util.Locale.ROOT)))continue;
                TextView row=text(scroll+"  ·  "+entry.optInt("fragment_count")+" fragments · "+entry.optInt("line_count")+" lines",15,ink,true);
                row.setBackground(shape(panel));LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,-2);p.setMargins(0,4,0,4);content.addView(row,p);
                row.setOnClickListener(v->{returnSection="DSS Transcription Archive";openEtcbcDssScroll(scroll);});
                shown++;
            }
            if(shown==0)content.addView(text("No scroll identifier matches this filter.",14,muted,false));
        }catch(Exception e){content.addView(text("The offline DSS transcription index is not present in this build. "+e.getMessage(),13,muted,false));}
    }

    void openEtcbcDssScroll(String scrollId){
        final String selected=scrollId;
        new android.os.AsyncTask<Void,Void,String>(){
            protected String doInBackground(Void... ignored){
                StringBuilder out=new StringBuilder();int count=0;
                try{
                    java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("dss/etcbc_transcriptions.jsonl"),"UTF-8"),65536);
                    String raw;
                    while((raw=reader.readLine())!=null){
                        org.json.JSONObject record=new org.json.JSONObject(raw);
                        if(!selected.equals(record.optString("scroll")))continue;
                        if(count==0){
                            out.append("Source: Martin G. Abegg Jr. transcriptions, ETCBC/CACCHT; structured export distributed by QDR.\n");
                            out.append("License: CC BY-NC 4.0 — non-commercial use only.\n");
                            out.append("Source revision: ").append(record.optString("source_revision")).append("\n");
                            out.append("Diplomatic display text is retained separately from normalized token text. Textual parallels are references, not part of this manuscript line.\n");
                            out.append("These are fragmentary source lines, not a continuous reconstructed text or an English translation. Fragment and line identifiers are retained.\n\n");
                        }
                        out.append("Fragment ").append(record.optString("fragment")).append(" · line ").append(record.optString("line")).append("\n");
                        out.append(record.optString("transcription_text")).append("\n");
                        String normalized=record.optString("normalized_text");
                        if(!normalized.isEmpty()&&!normalized.equals(record.optString("transcription_text")))out.append("Normalized token stream: ").append(normalized).append("\n");
                        org.json.JSONArray refs=record.optJSONArray("parallel_references");
                        if(refs!=null&&refs.length()>0){out.append("Textual parallels: ");for(int i=0;i<refs.length();i++){if(i>0)out.append("; ");out.append(refs.optString(i));}out.append("\n");}
                        out.append("\n");count++;
                    }
                    reader.close();
                    if(count==0)return "No line records found for "+selected+".";
                    return count+" source lines loaded.\n\n"+out.toString();
                }catch(Exception e){return "Unable to read the offline DSS transcription: "+e.getMessage();}
            }
            protected void onPostExecute(String result){
                TextView view=text(result,15,ink,false);enablePassageSelection(view);
                ScrollView sv=new ScrollView(MainActivity.this);sv.setPadding(12,8,12,8);sv.addView(view);
                new android.app.AlertDialog.Builder(MainActivity.this).setTitle(selected+" · ETCBC / Abegg").setView(sv)
                    .setNegativeButton("Back to scroll index",(d,w)->navigateTo("DSS Transcription Archive"))
                    .setPositiveButton("Close",null).show();
            }
        }.executeOnExecutor(android.os.AsyncTask.THREAD_POOL_EXECUTOR);
    }

    void openDssCatalogEntry(String item){
        try{
            java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("catalog/dead_sea_scrolls_register.json"),"UTF-8"));
            StringBuilder raw=new StringBuilder();String line;while((line=reader.readLine())!=null)raw.append(line);reader.close();
            org.json.JSONArray records=new org.json.JSONObject(raw.toString()).getJSONArray("records");
            String key=item.toLowerCase();String id="";
            if(key.contains("isaiah"))id="1QIsa-a";
            else if(key.contains("habakkuk"))id="1QpHab";
            else if(key.contains("genesis apocryphon"))id="1QapGen";
            else if(key.contains("community rule"))id="1QS";
            else if(key.contains("temple scroll"))id="11Q19";
            else if(key.contains("war scroll"))id="1QM";
            org.json.JSONObject match=null;
            for(int i=0;i<records.length();i++){org.json.JSONObject r=records.getJSONObject(i);if(r.optString("id").equals(id)){match=r;break;}}
            if(match==null){new android.app.AlertDialog.Builder(this).setTitle(item).setMessage("No verified DSS metadata record is available.").setPositiveButton("Close",null).show();return;}
            StringBuilder detail=new StringBuilder();
            detail.append("Cave: ").append(match.optString("cave")).append("\n");
            detail.append("Language: ").append(match.optString("language")).append("\n");
            detail.append("Material: ").append(match.optString("material")).append("\n");
            detail.append("Date: ").append(match.optString("date_estimate")).append("\n");
            detail.append("Dating basis: ").append(match.optString("date_basis")).append("\n");
            detail.append("Contents: ").append(match.optString("contents")).append("\n");
            detail.append("Condition: ").append(match.optString("condition")).append("\n");
            detail.append("Holding: ").append(match.optString("holding_institution")).append("\n");
            detail.append("Shelfmark: ").append(match.optString("shelfmark")).append("\n\n");
            detail.append("Status: ").append(match.optString("status")).append("\n\n");
            detail.append("Caution: ").append(match.optString("caution")).append("\n\n");
            detail.append("Image access: ").append(match.optString("image_access")).append("\n\n");
            detail.append("Sources:\n");org.json.JSONArray urls=match.optJSONArray("source_urls");
            if(urls!=null)for(int i=0;i<urls.length();i++)detail.append(urls.optString(i)).append("\n");
            TextView view=text(detail.toString(),14,ink,false);view.setAutoLinkMask(android.text.util.Linkify.WEB_URLS);view.setMovementMethod(android.text.method.LinkMovementMethod.getInstance());
            ScrollView sv=new ScrollView(this);sv.setPadding(14,8,14,8);sv.addView(view);
            android.app.AlertDialog.Builder builder=new android.app.AlertDialog.Builder(this).setTitle(match.optString("name")).setView(sv).setPositiveButton("Close",null);
            if("Sinaiticus".equalsIgnoreCase(match.optString("id")))builder.setNeutralButton("Open transcription",(d,w)->openSinaiticusArchive());
            builder.show();
        }catch(Exception e){new android.app.AlertDialog.Builder(this).setTitle("DSS catalogue unavailable").setMessage("The Dead Sea Scrolls metadata register is not present in this build.").setPositiveButton("Close",null).show();}
    }


    void openDssConcordanceEntry(String item){
        try{
            java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("catalog/dss_passage_concordance.json"),"UTF-8"));
            StringBuilder raw=new StringBuilder();String line;while((line=reader.readLine())!=null)raw.append(line);reader.close();
            org.json.JSONArray records=new org.json.JSONObject(raw.toString()).getJSONArray("records");
            String key=item.substring(0,item.indexOf(" — ")).trim();
            org.json.JSONObject match=null;
            for(int i=0;i<records.length();i++){org.json.JSONObject r=records.getJSONObject(i);if(r.optString("manuscript_id").equals(key)){match=r;break;}}
            if(match==null){new android.app.AlertDialog.Builder(this).setTitle(item).setMessage("No concordance record is available.").setPositiveButton("Close",null).show();return;}
            StringBuilder detail=new StringBuilder();
            ArrayList<int[]> translationRanges=new ArrayList<>();
            ArrayList<String> translationTexts=new ArrayList<>();
            ArrayList<String> translationRefs=new ArrayList<>();
            detail.append("Manuscript: ").append(match.optString("manuscript_id")).append("\n");
            detail.append("Work: ").append(match.optString("work")).append("\n");
            detail.append("Cave: ").append(match.optString("cave")).append("\n");
            detail.append("Language: ").append(match.optString("language")).append("\n");
            detail.append("IAA catalogue ID: ").append(match.optString("iaa_identifier")).append("\n");
            detail.append("IAA cross-reference: ").append(match.optString("iaa_cross_reference")).append("\n");
            detail.append("DJD reference: ").append(match.isNull("djd_reference")?"Not yet verified":match.optString("djd_reference")).append("\n\n");
            detail.append("Inventory references:\n");
            org.json.JSONArray inventory=match.optJSONArray("inventory_references");
            if(inventory!=null)for(int i=0;i<inventory.length();i++){org.json.JSONObject ref=inventory.getJSONObject(i);detail.append("• ").append(ref.optString("identifier")).append(" — ").append(ref.optString("note")).append("\n");}
            detail.append("\nReported passage coverage:\n");
            org.json.JSONArray passages=match.optJSONArray("passage_coverage");
            if(passages==null||passages.length()==0)detail.append("No passage range has been verified or recorded.\n");
            else for(int i=0;i<passages.length();i++){org.json.JSONObject p=passages.getJSONObject(i);detail.append("• ").append(p.optString("reference")).append("\n  Status: ").append(p.optString("coverage_status")).append("\n  Basis: ").append(p.optString("basis")).append("\n");}
            org.json.JSONArray fragmentGroups=match.optJSONArray("fragment_coverage");
            if(fragmentGroups!=null&&fragmentGroups.length()>0){
                detail.append("\nPublished fragment-to-passage mapping:\n");
                for(int i=0;i<fragmentGroups.length();i++){
                    org.json.JSONObject group=fragmentGroups.getJSONObject(i);
                    detail.append("• Fragment ").append(group.optString("fragment")).append(": ");
                    org.json.JSONArray refs=group.optJSONArray("passages");
                    if(refs!=null)for(int j=0;j<refs.length();j++){if(j>0)detail.append("; ");detail.append(refs.optString(j));}
                    detail.append("\n  Condition: ").append(group.optString("condition")).append("\n  Digital transcription display lines: ").append(group.optString("digital_transcription_line_range", "not recorded")).append(" (not manuscript column/line coordinates)\n  Basis: ").append(group.optString("basis")).append("\n");
                }
            }
            org.json.JSONArray lineMap=match.optJSONArray("transcription_line_map");
            if(lineMap!=null&&lineMap.length()>0){
                detail.append("\nDigital transcription line-by-line passage map:\n");
                for(int i=0;i<lineMap.length();i++){
                    org.json.JSONObject lineEntry=lineMap.getJSONObject(i);
                    detail.append("• ").append(lineEntry.optString("group")).append(", digital line ").append(lineEntry.optInt("digital_line")).append(": ");
                    org.json.JSONArray refs=lineEntry.optJSONArray("passages");
                    if(refs!=null)for(int j=0;j<refs.length();j++){if(j>0)detail.append("; ");detail.append(refs.optString(j));}
                    detail.append("\n  Hebrew transcription: ");
                    String lineText=lineEntry.optString("transcription_text", "");
                    int lineStart=detail.length();detail.append(lineText);int lineEnd=detail.length();
                    if(!lineText.isEmpty()){
                        translationRanges.add(new int[]{lineStart,lineEnd});translationTexts.add(lineText);
                        StringBuilder passageLabel=new StringBuilder();
                        if(refs!=null)for(int j=0;j<refs.length();j++){if(j>0)passageLabel.append("; ");passageLabel.append(refs.optString(j));}
                        translationRefs.add(passageLabel.length()>0?passageLabel.toString():lineEntry.optString("group")+" line "+lineEntry.optInt("digital_line"));
                    }
                    detail.append("\n  Source: ").append(lineEntry.optString("source_reference", "not recorded"));
                    if(lineEntry.has("note"))detail.append("\n  Note: ").append(lineEntry.optString("note"));
                    detail.append("\n");
                }
                detail.append("Mapping policy: ").append(match.optString("line_map_policy")).append("\n");
            }
            org.json.JSONArray additionalSources=match.optJSONArray("additional_transcription_sources");
            if(additionalSources!=null)for(int sourceIndex=0;sourceIndex<additionalSources.length();sourceIndex++){
                org.json.JSONObject source=additionalSources.getJSONObject(sourceIndex);
                detail.append("\nAdditional transcription source (kept separate):\n");
                detail.append(source.optString("title")).append("\n");
                detail.append("Provider: ").append(source.optString("provider")).append("\n");
                detail.append("Version: ").append(source.optString("version")).append("\n");
                detail.append("Format: ").append(source.optString("format")).append("\n");
                detail.append("Licence: ").append(source.optString("license")).append("\n");
                detail.append("Attribution: ").append(source.optString("attribution")).append("\n");
                detail.append("Source URL: ").append(source.optString("url")).append("\n");
                detail.append("Use: ").append(source.optString("use")).append("\n");
                detail.append("Caution: ").append(source.optString("caution")).append("\n");
                org.json.JSONArray sourceSections=source.optJSONArray("sections");
                if(sourceSections!=null)for(int sectionIndex=0;sectionIndex<sourceSections.length();sectionIndex++){
                    org.json.JSONObject section=sourceSections.getJSONObject(sectionIndex);
                    detail.append("\nFragment group: ").append(section.optString("fragment_group")).append("\n");
                    detail.append("PDF heading: ").append(section.optString("pdf_heading")).append("\n");
                    detail.append("Passage references: ");
                    org.json.JSONArray refs=section.optJSONArray("passage_refs");
                    if(refs!=null)for(int refIndex=0;refIndex<refs.length();refIndex++){if(refIndex>0)detail.append("; ");detail.append(refs.optString(refIndex));}
                    detail.append("\nTranscription text (PDF text layer):\n");
                    String sectionText=section.optString("pdf_text_lines", "");
                    int sectionStart=detail.length();detail.append(sectionText);int sectionEnd=detail.length();
                    if(!sectionText.isEmpty()){
                        translationRanges.add(new int[]{sectionStart,sectionEnd});translationTexts.add(sectionText);
                        StringBuilder passageLabel=new StringBuilder();
                        if(refs!=null)for(int j=0;j<refs.length();j++){if(j>0)passageLabel.append("; ");passageLabel.append(refs.optString(j));}
                        translationRefs.add(passageLabel.length()>0?passageLabel.toString():section.optString("fragment_group"));
                    }
                    detail.append("\n");
                    detail.append("Section caution: ").append(section.optString("caution")).append("\n");
                }
            }
            org.json.JSONArray columns=match.optJSONArray("column_coverage");
            if(columns!=null&&columns.length()>0){
                detail.append("\nPublished column-to-passage concordance:\n");
                for(int i=0;i<columns.length();i++){
                    org.json.JSONObject col=columns.getJSONObject(i);
                    detail.append("• Column ").append(col.optString("column")).append(": ");
                    org.json.JSONArray refs=col.optJSONArray("passages");
                    if(refs!=null)for(int j=0;j<refs.length();j++){if(j>0)detail.append("; ");detail.append(refs.optString(j));}
                    detail.append("\n");
                }
                detail.append("Basis: ").append(columns.getJSONObject(0).optString("basis")).append("\n");
            }
            org.json.JSONObject edition=match.optJSONObject("published_edition");
            if(edition!=null){
                detail.append("\nPublished edition: ").append(edition.optString("reference")).append("\n");
                detail.append("Editor: ").append(edition.optString("editor")).append("\n");
                detail.append("Bibliography: ").append(edition.optString("bibliography")).append("\n");
                detail.append("Edition caution: ").append(edition.optString("caution")).append("\n");
            }
            org.json.JSONObject groupIndex=match.optJSONObject("fragment_group_index");
            if(groupIndex!=null){
                detail.append("\nDigital fragment-group index: ").append(groupIndex.optInt("display_group_count")).append(" groups\n");
                org.json.JSONArray groupNames=groupIndex.optJSONArray("groups");
                if(groupNames!=null)for(int i=0;i<groupNames.length();i++)detail.append("• ").append(groupNames.optString(i)).append(i==groupNames.length()-1?"\n":"; ");
                detail.append("Index source: ").append(groupIndex.optString("source")).append("\n");
            }
            detail.append("\nStatus: ").append(match.optString("status")).append("\n");
            org.json.JSONObject transcription=match.optJSONObject("transcription_source");
            if(transcription!=null){
                detail.append("\nHebrew transcription source:\n").append(transcription.optString("title")).append("\n");
                detail.append("Provider: ").append(transcription.optString("provider")).append("\n");
                detail.append("Version: ").append(transcription.optString("version")).append("\n");
                detail.append("License: ").append(transcription.optString("license")).append("\n");
                detail.append("Attribution: ").append(transcription.optString("attribution")).append("\n");
                detail.append("Source URL: ").append(transcription.optString("url")).append("\n");
                detail.append("Use: ").append(transcription.optString("use")).append("\n");
                detail.append("Transcription caution: ").append(transcription.optString("caution")).append("\n");
            }
            detail.append("Caution: ").append(match.optString("caution")).append("\n");
            TextView view=text(detail.toString(),14,ink,false);
            android.text.SpannableString clickableText=new android.text.SpannableString(detail.toString());
            for(int spanIndex=0;spanIndex<translationRanges.size();spanIndex++){
                final String selectedText=translationTexts.get(spanIndex);
                final String selectedReference=translationRefs.get(spanIndex);
                int[] range=translationRanges.get(spanIndex);
                clickableText.setSpan(new android.text.style.ClickableSpan(){
                    @Override public void onClick(View widget){openAiTranslator(selectedReference,selectedText,"he");}
                    @Override public void updateDrawState(android.text.TextPaint paint){paint.setColor(gold);paint.setUnderlineText(true);}
                },range[0],range[1],android.text.Spanned.SPAN_EXCLUSIVE_EXCLUSIVE);
            }
            view.setText(clickableText);view.setAutoLinkMask(android.text.util.Linkify.WEB_URLS);view.setMovementMethod(android.text.method.LinkMovementMethod.getInstance());
            ScrollView sv=new ScrollView(this);sv.setPadding(14,8,14,8);sv.addView(view);
            new android.app.AlertDialog.Builder(this).setTitle(match.optString("manuscript_id")).setView(sv).setPositiveButton("Close",null).show();
        }catch(Exception e){new android.app.AlertDialog.Builder(this).setTitle("Concordance unavailable").setMessage("The DSS passage concordance is not present in this build.").setPositiveButton("Close",null).show();}
    }

    void openSinaiticusArchive(){
        try{
            java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("sinaiticus/sinaiticus_index.json"),"UTF-8"));
            StringBuilder raw=new StringBuilder();String line;while((line=reader.readLine())!=null)raw.append(line);reader.close();
            org.json.JSONObject index=new org.json.JSONObject(raw.toString());
            org.json.JSONArray pages=index.getJSONArray("pages");
            String[] labels=new String[pages.length()];
            String[] ids=new String[pages.length()];
            for(int i=0;i<pages.length();i++){
                org.json.JSONObject page=pages.getJSONObject(i);
                ids[i]=page.optString("page_id");
                labels[i]=ids[i]+"  ·  "+page.optInt("column_count")+" columns · "+page.optInt("line_count")+" lines";
            }
            new android.app.AlertDialog.Builder(this).setTitle("Codex Sinaiticus · Page Archive")
                .setItems(labels,(dialog,which)->openSinaiticusPage(ids[which]))
                .setNegativeButton("Close",null).show();
        }catch(Exception e){
            new android.app.AlertDialog.Builder(this).setTitle("Transcription unavailable")
                .setMessage("The Codex Sinaiticus transcription was not generated in this build. "+e.getMessage())
                .setPositiveButton("Close",null).show();
        }
    }

    void openSinaiticusPage(String pageId){
        final String selected=pageId;
        new android.os.AsyncTask<Void,Void,String>(){
            protected String doInBackground(Void... ignored){
                StringBuilder out=new StringBuilder();
                int count=0;
                try{
                    java.io.BufferedReader indexReader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("sinaiticus/sinaiticus_index.json"),"UTF-8"));
                    StringBuilder indexRaw=new StringBuilder();String indexLine;
                    while((indexLine=indexReader.readLine())!=null)indexRaw.append(indexLine);
                    indexReader.close();
                    org.json.JSONArray pages=new org.json.JSONObject(indexRaw.toString()).getJSONArray("pages");
                    String assetPath=null;
                    for(int i=0;i<pages.length();i++){
                        org.json.JSONObject page=pages.getJSONObject(i);
                        if(selected.equals(page.optString("page_id"))){assetPath=page.optString("asset_file");break;}
                    }
                    if(assetPath==null)return "No offline page file is indexed for "+selected+".";
                    java.io.BufferedReader reader=new java.io.BufferedReader(
                        new java.io.InputStreamReader(
                            new java.util.zip.GZIPInputStream(getAssets().open(assetPath)),"UTF-8"),8192);
                    String raw;
                    while((raw=reader.readLine())!=null){
                        org.json.JSONObject record=new org.json.JSONObject(raw);
                        if(count==0)out.append("Source: Codex Sinaiticus Project / ITSEE XML transcription\n")
                            .append("Licence: CC BY-NC-SA 3.0 — non-commercial use; adaptations share alike.\n")
                            .append("Original page, column, line, and word identifiers are preserved.\n\n");
                        out.append(record.optString("column_id")).append(" · ").append(record.optString("line_id")).append("\n");
                        out.append(record.optString("text")).append("\n\n");
                        count++;
                    }
                    reader.close();
                    return count==0?"No transcription lines were found for "+selected+".":count+" manuscript lines\n\n"+out.toString();
                }catch(Exception e){return "Unable to read the offline Codex Sinaiticus transcription: "+e.getMessage();}
            }
            protected void onPostExecute(String result){
                TextView view=text(result,15,ink,false);enablePassageSelection(view);
                ScrollView sv=new ScrollView(MainActivity.this);sv.setPadding(12,8,12,8);sv.addView(view);
                new android.app.AlertDialog.Builder(MainActivity.this).setTitle(selected+" · Codex Sinaiticus")
                    .setView(sv).setNegativeButton("Back to page index",(d,w)->openSinaiticusArchive())
                    .setPositiveButton("Close",null).show();
            }
        }.executeOnExecutor(android.os.AsyncTask.THREAD_POOL_EXECUTOR);
    }

    void openDidacheArchive(){
        try{
            java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("other_reference/didache/didache_index.json"),"UTF-8"));
            StringBuilder raw=new StringBuilder();String line;while((line=reader.readLine())!=null)raw.append(line);reader.close();
            org.json.JSONObject index=new org.json.JSONObject(raw.toString());
            org.json.JSONArray chapters=index.getJSONArray("chapters");
            int[] numbers=new int[chapters.length()];
            String[] labels=new String[chapters.length()];
            for(int i=0;i<chapters.length();i++){
                org.json.JSONObject item=chapters.getJSONObject(i);
                numbers[i]=item.optInt("chapter");
                labels[i]="Chapter "+numbers[i]+"  ·  "+item.optInt("section_count")+" sections";
            }
            new android.app.AlertDialog.Builder(this).setTitle("Didache · Greek text")
                .setItems(labels,(dialog,which)->openDidacheChapter(numbers[which]))
                .setNegativeButton("Close",null).show();
        }catch(Exception e){
            showInfo("Didache text unavailable","The offline Greek Didache text was not generated in this build. "+e.getMessage());
        }
    }

    void openDidacheChapter(int chapter){
        new android.os.AsyncTask<Void,Void,String>(){
            protected String doInBackground(Void... ignored){
                StringBuilder out=new StringBuilder();int count=0;
                try{
                    java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("other_reference/didache/didache_greek.jsonl"),"UTF-8"),8192);
                    String raw;
                    while((raw=reader.readLine())!=null){
                        org.json.JSONObject record=new org.json.JSONObject(raw);
                        if(record.optInt("chapter")!=chapter)continue;
                        if(count==0)out.append("Source: Kirsopp Lake, The Apostolic Fathers, volume 1 (1912), Didache Greek text\n")
                            .append("Digital edition: Open Greek and Latin / First1KGreek\n")
                            .append("Licence: CC BY-SA 4.0\n")
                            .append("Textual basis: printed Greek edition, not a direct diplomatic transcription of Codex Hierosolymitanus 54\n")
                            .append("No missing wording is reconstructed.\n\n");
                        out.append(record.optString("reference")).append("\n");
                        org.json.JSONArray pages=record.optJSONArray("source_pages");
                        if(pages!=null&&pages.length()>0)out.append("Printed page marker(s): ").append(pages.toString()).append("\n");
                        out.append(record.optString("text")).append("\n");
                        org.json.JSONArray refs=record.optJSONArray("cross_references");
                        if(refs!=null&&refs.length()>0){
                            out.append("Source cross-references:\n");
                            for(int i=0;i<refs.length();i++){
                                org.json.JSONObject ref=refs.getJSONObject(i);
                                out.append("• ").append(ref.optString("text"));
                                if(!ref.optString("corresp").isEmpty())out.append(" [").append(ref.optString("corresp")).append("]");
                                out.append("\n");
                            }
                        }
                        org.json.JSONArray notes=record.optJSONArray("editorial_notes");
                        if(notes!=null)for(int i=0;i<notes.length();i++){
                            org.json.JSONObject note=notes.getJSONObject(i);
                            out.append("Edition note: ").append(note.optString("text")).append("\n");
                        }
                        out.append("\n");count++;
                    }
                    reader.close();
                    return count==0?"No source sections were found for Didache chapter "+chapter+".":count+" Greek sections\n\n"+out.toString();
                }catch(Exception e){return "Unable to read the offline Didache text: "+e.getMessage();}
            }
            protected void onPostExecute(String result){
                TextView view=text(result,15,ink,false);enablePassageSelection(view);
                ScrollView sv=new ScrollView(MainActivity.this);sv.setPadding(12,8,12,8);sv.addView(view);
                new android.app.AlertDialog.Builder(MainActivity.this).setTitle("Didache · Chapter "+chapter)
                    .setView(sv).setNegativeButton("Back to chapters",(d,w)->openDidacheArchive())
                    .setPositiveButton("Close",null).show();
            }
        }.executeOnExecutor(android.os.AsyncTask.THREAD_POOL_EXECUTOR);
    }

    void openThomasArchive(){
        try{
            java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("other_reference/thomas/thomas_index.json"),"UTF-8"));
            StringBuilder raw=new StringBuilder();String line;while((line=reader.readLine())!=null)raw.append(line);reader.close();
            org.json.JSONObject index=new org.json.JSONObject(raw.toString());
            org.json.JSONArray pageArray=index.getJSONArray("pages");
            String[] labels=new String[pageArray.length()];int[] pages=new int[pageArray.length()];
            for(int i=0;i<pageArray.length();i++){pages[i]=pageArray.getInt(i);labels[i]="Codex page "+pages[i];}
            new android.app.AlertDialog.Builder(this).setTitle("Gospel of Thomas · Coptic manuscript text")
                .setItems(labels,(dialog,which)->openThomasPage(pages[which]))
                .setNegativeButton("Close",null).show();
        }catch(Exception e){
            showInfo("Gospel of Thomas unavailable","The offline Coptic text was not generated in this build. "+e.getMessage());
        }
    }

    void openThomasPage(int page){
        new android.os.AsyncTask<Void,Void,String>(){
            protected String doInBackground(Void... ignored){
                StringBuilder out=new StringBuilder();int count=0;
                try{
                    java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("other_reference/thomas/thomas_coptic.jsonl"),"UTF-8"),8192);
                    String raw;
                    while((raw=reader.readLine())!=null){
                        org.json.JSONObject record=new org.json.JSONObject(raw);
                        if(!record.optString("page").equals(String.valueOf(page)))continue;
                        if(count==0)out.append("Manuscript: Nag Hammadi Codex II, tractate 2; Coptic Museum, Cairo, NH 10544\n")
                            .append("Language: Sahidic Coptic with Lycopolitan features\n")
                            .append("Edition: Paul C. Dilley, Coptic SCRIPTORIUM v6.2.0 (2025-11-25)\n")
                            .append("Licence: CC BY 4.0\n")
                            .append("Textual basis: digital scholarly edition based on examination of the codex facsimile\n")
                            .append("The Greek papyrus fragments are separate witnesses and are not included here. Missing wording is not reconstructed.\n\n");
                        out.append("Saying ").append(record.optString("saying","prologue"));
                        if(!record.optString("paragraph").isEmpty())out.append(" · paragraph ").append(record.optString("paragraph"));
                        out.append("\nCodex page ").append(record.optString("page"));
                        if(!record.optString("column").isEmpty())out.append(", column ").append(record.optString("column"));
                        if(!record.optString("line").isEmpty())out.append(", line ").append(record.optString("line"));
                        out.append("\n").append(record.optString("text")).append("\n\n");
                        count++;
                    }
                    reader.close();
                    return count==0?"No Coptic text records were found for codex page "+page+".":count+" manuscript line records\n\n"+out.toString();
                }catch(Exception e){return "Unable to read the offline Coptic text: "+e.getMessage();}
            }
            protected void onPostExecute(String result){
                TextView view=text(result,15,ink,false);enablePassageSelection(view);
                ScrollView sv=new ScrollView(MainActivity.this);sv.setPadding(12,8,12,8);sv.addView(view);
                new android.app.AlertDialog.Builder(MainActivity.this).setTitle("Gospel of Thomas · Page "+page)
                    .setView(sv).setNegativeButton("Back to pages",(d,w)->openThomasArchive())
                    .setPositiveButton("Close",null).show();
            }
        }.executeOnExecutor(android.os.AsyncTask.THREAD_POOL_EXECUTOR);
    }

    void openHermasArchive(){
        try{
            java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("other_reference/hermas/hermas_index.json"),"UTF-8"));
            StringBuilder raw=new StringBuilder();String line;while((line=reader.readLine())!=null)raw.append(line);reader.close();
            org.json.JSONObject index=new org.json.JSONObject(raw.toString());
            org.json.JSONArray books=index.getJSONArray("books");
            int[] numbers=new int[books.length()];
            String[] labels=new String[books.length()];
            for(int i=0;i<books.length();i++){
                org.json.JSONObject book=books.getJSONObject(i);
                numbers[i]=book.optInt("book");
                String title=book.optString("book_title");
                labels[i]=book.optString("part_type")+" "+numbers[i]+"  ·  "+book.optInt("section_count")+" sections";
                if(!title.isEmpty())labels[i]+="  ·  "+title;
            }
            new android.app.AlertDialog.Builder(this).setTitle("Shepherd of Hermas · Greek text")
                .setItems(labels,(dialog,which)->openHermasBook(numbers[which]))
                .setNegativeButton("Close",null).show();
        }catch(Exception e){
            showInfo("Shepherd of Hermas text unavailable","The offline Greek text was not generated in this build. "+e.getMessage());
        }
    }

    void openHermasBook(int book){
        new android.os.AsyncTask<Void,Void,String>(){
            protected String doInBackground(Void... ignored){
                StringBuilder out=new StringBuilder();int count=0;
                try{
                    java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("other_reference/hermas/hermas_greek.jsonl"),"UTF-8"),8192);
                    String raw;
                    while((raw=reader.readLine())!=null){
                        org.json.JSONObject record=new org.json.JSONObject(raw);
                        if(record.optInt("book")!=book)continue;
                        if(count==0)out.append("Source: Kirsopp Lake, The Apostolic Fathers, volume 2 (1917), Shepherd of Hermas Greek text\n")
                            .append("Digital edition: Open Greek and Latin / First1KGreek\n")
                            .append("Licence: CC BY-SA 4.0\n")
                            .append("Textual basis: printed Greek edition, not a direct diplomatic transcription of one manuscript\n")
                            .append("No missing wording is reconstructed.\n\n");
                        out.append(record.optString("reference")).append("\n");
                        org.json.JSONArray pages=record.optJSONArray("source_pages");
                        if(pages!=null&&pages.length()>0)out.append("Printed page marker(s): ").append(pages.toString()).append("\n");
                        out.append(record.optString("text")).append("\n");
                        org.json.JSONArray refs=record.optJSONArray("cross_references");
                        if(refs!=null&&refs.length()>0){
                            out.append("Source cross-references:\n");
                            for(int i=0;i<refs.length();i++){
                                org.json.JSONObject ref=refs.getJSONObject(i);
                                out.append("• ").append(ref.optString("text"));
                                if(!ref.optString("corresp").isEmpty())out.append(" [").append(ref.optString("corresp")).append("]");
                                out.append("\n");
                            }
                        }
                        org.json.JSONArray notes=record.optJSONArray("editorial_notes");
                        if(notes!=null)for(int i=0;i<notes.length();i++){
                            org.json.JSONObject note=notes.getJSONObject(i);
                            out.append("Edition note: ").append(note.optString("text")).append("\n");
                        }
                        out.append("\n");count++;
                    }
                    reader.close();
                    return count==0?"No source sections were found for Hermas book "+book+".":count+" Greek sections\n\n"+out.toString();
                }catch(Exception e){return "Unable to read the offline Shepherd of Hermas text: "+e.getMessage();}
            }
            protected void onPostExecute(String result){
                TextView view=text(result,15,ink,false);enablePassageSelection(view);
                ScrollView sv=new ScrollView(MainActivity.this);sv.setPadding(12,8,12,8);sv.addView(view);
                new android.app.AlertDialog.Builder(MainActivity.this).setTitle("Shepherd of Hermas · Book "+book)
                    .setView(sv).setNegativeButton("Back to divisions",(d,w)->openHermasArchive())
                    .setPositiveButton("Close",null).show();
            }
        }.executeOnExecutor(android.os.AsyncTask.THREAD_POOL_EXECUTOR);
    }

    void openJubileesGeezArchive(){
        try{
            java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("other_reference/jubilees_geez/jubilees_geez_index.json"),"UTF-8"));
            StringBuilder raw=new StringBuilder();String line;while((line=reader.readLine())!=null)raw.append(line);reader.close();
            org.json.JSONArray editions=new org.json.JSONObject(raw.toString()).getJSONArray("editions");
            String[] labels=new String[editions.length()];String[] ids=new String[editions.length()];
            for(int i=0;i<editions.length();i++){org.json.JSONObject e=editions.getJSONObject(i);ids[i]=e.optString("edition");labels[i]=e.optString("title")+" · "+e.optInt("chapter_count")+" chapters";}
            new android.app.AlertDialog.Builder(this).setTitle("Jubilees · Ge'ez editions").setItems(labels,(d,w)->openJubileesGeezEdition(ids[w])).setNegativeButton("Close",null).show();
        }catch(Exception e){showInfo("Jubilees Ge'ez text unavailable","The offline Ge'ez editions were not generated in this build. "+e.getMessage());}
    }
    void openJubileesGeezEdition(String edition){
        try{
            java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("other_reference/jubilees_geez/jubilees_geez_index.json"),"UTF-8"));
            StringBuilder raw=new StringBuilder();String line;while((line=reader.readLine())!=null)raw.append(line);reader.close();
            org.json.JSONArray editions=new org.json.JSONObject(raw.toString()).getJSONArray("editions");org.json.JSONObject selected=null;
            for(int i=0;i<editions.length();i++)if(edition.equals(editions.getJSONObject(i).optString("edition")))selected=editions.getJSONObject(i);
            if(selected==null)return;
            org.json.JSONArray chapters=selected.getJSONArray("chapters");int[] nums=new int[chapters.length()];String[] labels=new String[chapters.length()];
            for(int i=0;i<chapters.length();i++){nums[i]=chapters.getInt(i);labels[i]="Chapter "+nums[i];}
            new android.app.AlertDialog.Builder(this).setTitle(selected.optString("title")).setItems(labels,(d,w)->openJubileesGeezChapter(edition,nums[w])).setNegativeButton("Back to editions",(d,w)->openJubileesGeezArchive()).show();
        }catch(Exception e){showInfo("Jubilees index unavailable",e.getMessage());}
    }
    void openJubileesGeezChapter(String edition,int chapter){
        new android.os.AsyncTask<Void,Void,String>(){
            protected String doInBackground(Void... ignored){
                StringBuilder out=new StringBuilder();int count=0;
                try{
                    java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("other_reference/jubilees_geez/jubilees_geez.jsonl"),"UTF-8"),8192);
                    String raw;while((raw=reader.readLine())!=null){
                        org.json.JSONObject record=new org.json.JSONObject(raw);
                        if(!edition.equals(record.optString("edition"))||record.optInt("chapter")!=chapter)continue;
                        if(count==0)out.append(record.optString("edition_title")).append("\n").append("Source: Beta maṣāḥǝft, LIT1697Jubilees.xml\nLanguage: Ge'ez\nLicence: CC BY-SA 4.0\n").append(record.optString("edition_basis")).append("\nEdition-based text, not a fresh diplomatic transcription of a named manuscript. The two Ge'ez editions and Qumran Hebrew fragments remain separate.\n\n");
                        out.append(record.optString("reference")).append("\n").append(record.optString("text")).append("\n\n");count++;
                    }reader.close();
                    return count==0?"No Ge'ez text records found for this chapter.":count+" numbered text records\n\n"+out.toString();
                }catch(Exception e){return "Unable to read the offline Ge'ez Jubilees text: "+e.getMessage();}
            }
            protected void onPostExecute(String result){
                TextView view=text(result,15,ink,false);enablePassageSelection(view);
                ScrollView sv=new ScrollView(MainActivity.this);sv.setPadding(12,8,12,8);sv.addView(view);
                new android.app.AlertDialog.Builder(MainActivity.this).setTitle("Jubilees · Chapter "+chapter).setView(sv).setNegativeButton("Back to chapters",(d,w)->openJubileesGeezEdition(edition)).setPositiveButton("Close",null).show();
            }
        }.executeOnExecutor(android.os.AsyncTask.THREAD_POOL_EXECUTOR);
    }

    void openTwelvePatriarchsArchive(){
        try{
            java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("other_reference/twelve_patriarchs/twelve_patriarchs_index.json"),"UTF-8"));
            StringBuilder raw=new StringBuilder();String line;while((line=reader.readLine())!=null)raw.append(line);reader.close();
            org.json.JSONArray testaments=new org.json.JSONObject(raw.toString()).getJSONArray("testaments");
            String[] names=new String[testaments.length()];String[] labels=new String[testaments.length()];
            for(int i=0;i<testaments.length();i++){org.json.JSONObject t=testaments.getJSONObject(i);names[i]=t.optString("name");labels[i]=t.optString("label")+" · "+t.optInt("chapter_count")+" chapters";}
            new android.app.AlertDialog.Builder(this).setTitle("Testaments of the Twelve Patriarchs · Greek")
                .setItems(labels,(d,w)->openTwelvePatriarchsTestament(names[w])).setNegativeButton("Close",null).show();
        }catch(Exception e){showInfo("Greek text unavailable","The offline Greek base text was not generated in this build. "+e.getMessage());}
    }
    void openTwelvePatriarchsTestament(String testament){
        try{
            java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("other_reference/twelve_patriarchs/twelve_patriarchs_index.json"),"UTF-8"));
            StringBuilder raw=new StringBuilder();String line;while((line=reader.readLine())!=null)raw.append(line);reader.close();
            org.json.JSONArray testaments=new org.json.JSONObject(raw.toString()).getJSONArray("testaments");org.json.JSONObject selected=null;
            for(int i=0;i<testaments.length();i++){org.json.JSONObject t=testaments.getJSONObject(i);if(testament.equals(t.optString("name"))){selected=t;break;}}
            if(selected==null)throw new Exception("Testament not found in index.");
            org.json.JSONArray chapters=selected.getJSONArray("chapters");String[] nums=new String[chapters.length()];String[] labels=new String[chapters.length()];
            for(int i=0;i<chapters.length();i++){nums[i]=chapters.getString(i);labels[i]="Chapter "+nums[i];}
            new android.app.AlertDialog.Builder(this).setTitle("Testament of "+testament+" · Chapters")
                .setItems(labels,(d,w)->openTwelvePatriarchsChapter(testament,nums[w]))
                .setNegativeButton("Back to testaments",(d,w)->openTwelvePatriarchsArchive()).show();
        }catch(Exception e){showInfo("Chapter index unavailable","Unable to open this testament. "+e.getMessage());}
    }
    void openTwelvePatriarchsChapter(String testament,String chapter){
        new android.os.AsyncTask<Void,Void,String>(){
            protected String doInBackground(Void... ignored){
                StringBuilder out=new StringBuilder();int count=0;
                try{
                    java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("other_reference/twelve_patriarchs/twelve_patriarchs_greek.jsonl"),"UTF-8"),8192);
                    String raw;while((raw=reader.readLine())!=null){
                        org.json.JSONObject record=new org.json.JSONObject(raw);
                        if(!testament.equals(record.optString("testament"))||!chapter.equals(record.optString("chapter")))continue;
                        if(count==0)out.append("Language: Ancient Greek\nLicense: CC BY 4.0\n")
                            .append("Source: Online Critical Pseudepigrapha, Greek Wikisource base text\n")
                            .append("Textual status: provisional single-witness base text; not yet collated against R. H. Charles (1908), as stated by the source. Not a diplomatic transcription of a named ancient codex.\n\n");
                        out.append(record.optString("reference")).append("\n").append(record.optString("text")).append("\n\n");count++;
                    }reader.close();return count==0?"No Greek verse records found for this chapter.":count+" Greek verse records\n\n"+out.toString();
                }catch(Exception e){return "Unable to read the offline Greek text: "+e.getMessage();}
            }
            protected void onPostExecute(String result){
                TextView view=text(result,15,ink,false);enablePassageSelection(view);
                ScrollView sv=new ScrollView(MainActivity.this);sv.setPadding(12,8,12,8);sv.addView(view);
                new android.app.AlertDialog.Builder(MainActivity.this).setTitle("Testament of "+testament+" · "+chapter).setView(sv)
                    .setNegativeButton("Back to chapters",(d,w)->openTwelvePatriarchsTestament(testament)).setPositiveButton("Close",null).show();
            }
        }.executeOnExecutor(android.os.AsyncTask.THREAD_POOL_EXECUTOR);
    }

    void openBarnabasArchive(){
        try{
            java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("other_reference/barnabas/barnabas_index.json"),"UTF-8"));
            StringBuilder raw=new StringBuilder();String line;while((line=reader.readLine())!=null)raw.append(line);reader.close();
            org.json.JSONArray chapters=new org.json.JSONObject(raw.toString()).getJSONArray("chapters");
            String[] numbers=new String[chapters.length()];String[] labels=new String[chapters.length()];
            for(int i=0;i<chapters.length();i++){
                org.json.JSONObject chapter=chapters.getJSONObject(i);numbers[i]=chapter.optString("chapter");
                labels[i]="Chapter "+numbers[i]+" · "+chapter.optInt("section_count")+" sections";
            }
            new android.app.AlertDialog.Builder(this).setTitle("Epistle of Barnabas · Greek")
                .setItems(labels,(d,w)->openBarnabasChapter(numbers[w])).setNegativeButton("Close",null).show();
        }catch(Exception e){showInfo("Barnabas Greek text unavailable","The offline text was not generated in this build. "+e.getMessage());}
    }

    void openBarnabasChapter(String chapter){
        new android.os.AsyncTask<Void,Void,String>(){
            protected String doInBackground(Void... ignored){
                StringBuilder out=new StringBuilder();int count=0;
                try{
                    java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("other_reference/barnabas/barnabas_greek.jsonl"),"UTF-8"),8192);
                    String raw;
                    while((raw=reader.readLine())!=null){
                        org.json.JSONObject record=new org.json.JSONObject(raw);
                        if(!chapter.equals(record.optString("chapter")))continue;
                        if(count==0)out.append("Source: Kirsopp Lake, The Apostolic Fathers, volume 1 (1912)\n")
                            .append("Digital edition: Perseus Digital Library / Open Greek and Latin First1KGreek\n")
                            .append("License: CC BY-SA 4.0\n")
                            .append("Textual basis: printed Greek edition, not a direct diplomatic transcription of one ancient manuscript.\n")
                            .append("Editorial notes and cross-references are separate from the Greek text.\n\n");
                        out.append(record.optString("reference")).append("\n");
                        org.json.JSONArray pages=record.optJSONArray("source_pages");
                        if(pages!=null&&pages.length()>0){out.append("Printed pages: ");for(int p=0;p<pages.length();p++){if(p>0)out.append(", ");out.append(pages.optString(p));}out.append("\n");}
                        out.append(record.optString("text")).append("\n\n");
                        org.json.JSONArray notes=record.optJSONArray("editorial_notes");
                        if(notes!=null&&notes.length()>0){out.append("Editorial notes:\n");for(int n=0;n<notes.length();n++){org.json.JSONObject note=notes.getJSONObject(n);out.append("- ").append(note.optString("text")).append("\n");}out.append("\n");}
                        org.json.JSONArray refs=record.optJSONArray("cross_references");
                        if(refs!=null&&refs.length()>0){out.append("Cross-references:\n");for(int n=0;n<refs.length();n++){org.json.JSONObject ref=refs.getJSONObject(n);out.append("- ").append(ref.optString("text")).append("\n");}out.append("\n");}
                        count++;
                    }
                    reader.close();
                }catch(Exception e){return "Unable to read the offline Barnabas Greek text: "+e.getMessage();}
                return count==0?"No sections were found for this chapter.":count+" sections\n\n"+out.toString()+"\nNo missing wording is reconstructed.";
            }
            protected void onPostExecute(String result){
                TextView view=text(result,15,ink,false);enablePassageSelection(view);
                ScrollView sv=new ScrollView(MainActivity.this);sv.setPadding(12,8,12,8);sv.addView(view);
                new android.app.AlertDialog.Builder(MainActivity.this).setTitle("Barnabas · Chapter "+chapter).setView(sv)
                    .setNegativeButton("Back to chapters",(d,w)->openBarnabasArchive()).setPositiveButton("Close",null).show();
            }
        }.executeOnExecutor(android.os.AsyncTask.THREAD_POOL_EXECUTOR);
    }

    void openIgnatiusArchive(){
        try{
            java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("other_reference/ignatius/ignatius_index.json"),"UTF-8"));
            StringBuilder raw=new StringBuilder();String line;while((line=reader.readLine())!=null)raw.append(line);reader.close();
            org.json.JSONArray letters=new org.json.JSONObject(raw.toString()).getJSONArray("letters");
            String[] numbers=new String[letters.length()];String[] labels=new String[letters.length()];
            for(int i=0;i<letters.length();i++){
                org.json.JSONObject letter=letters.getJSONObject(i);numbers[i]=letter.optString("number");
                labels[i]=letter.optString("name")+" · "+letter.optInt("chapter_count")+" chapters · "+letter.optInt("section_count")+" sections";
            }
            new android.app.AlertDialog.Builder(this).setTitle("Ignatius of Antioch · Greek letters")
                .setItems(labels,(d,w)->openIgnatiusLetter(numbers[w])).setNegativeButton("Close",null).show();
        }catch(Exception e){showInfo("Ignatius Greek text unavailable","The offline Greek text was not generated in this build. "+e.getMessage());}
    }

    void openIgnatiusLetter(String letterNo){
        try{
            java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("other_reference/ignatius/ignatius_index.json"),"UTF-8"));
            StringBuilder raw=new StringBuilder();String line;while((line=reader.readLine())!=null)raw.append(line);reader.close();
            org.json.JSONArray letters=new org.json.JSONObject(raw.toString()).getJSONArray("letters");
            org.json.JSONObject selected=null;
            for(int i=0;i<letters.length();i++){org.json.JSONObject item=letters.getJSONObject(i);if(item.optString("number").equals(letterNo)){selected=item;break;}}
            if(selected==null)throw new Exception("Letter index not found.");
            org.json.JSONArray chapters=selected.getJSONArray("chapters");String[] numbers=new String[chapters.length()];String[] labels=new String[chapters.length()];
            for(int i=0;i<chapters.length();i++){
                org.json.JSONObject chapter=chapters.getJSONObject(i);numbers[i]=chapter.optString("chapter");
                labels[i]=(numbers[i].equals("praef")?"Preface":"Chapter "+numbers[i])+" · "+chapter.optInt("section_count")+" sections";
            }
            String title=selected.optString("name");
            new android.app.AlertDialog.Builder(this).setTitle(title+" · Greek text")
                .setItems(labels,(d,w)->openIgnatiusChapter(letterNo,numbers[w]))
                .setNegativeButton("Back to letters",(d,w)->openIgnatiusArchive()).setPositiveButton("Close",null).show();
        }catch(Exception e){showInfo("Ignatius letter unavailable",e.getMessage());}
    }

    void openIgnatiusChapter(String letterNo,String chapter){
        new android.os.AsyncTask<Void,Void,String>(){
            protected String doInBackground(Void... ignored){
                StringBuilder out=new StringBuilder();int count=0;
                try{
                    java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("other_reference/ignatius/ignatius_greek.jsonl"),"UTF-8"),8192);
                    String raw;
                    while((raw=reader.readLine())!=null){
                        org.json.JSONObject record=new org.json.JSONObject(raw);
                        if(!letterNo.equals(record.optString("letter"))||!chapter.equals(record.optString("chapter")))continue;
                        if(count==0)out.append("Source: Kirsopp Lake, The Apostolic Fathers, volume 1 (1912)\n")
                            .append("Digital edition: Perseus Digital Library / Open Greek and Latin First1KGreek\n")
                            .append("License: CC BY-SA 4.0\n")
                            .append("Textual basis: printed Greek edition, not a direct diplomatic transcription of one ancient manuscript.\n")
                            .append("Editorial notes and cross-references are stored separately from the Greek text.\n\n");
                        out.append(record.optString("reference")).append("\n");
                        org.json.JSONArray pages=record.optJSONArray("source_pages");
                        if(pages!=null&&pages.length()>0){out.append("Printed pages: ");for(int p=0;p<pages.length();p++){if(p>0)out.append(", ");out.append(pages.optString(p));}out.append("\n");}
                        out.append(record.optString("text")).append("\n\n");
                        org.json.JSONArray notes=record.optJSONArray("editorial_notes");
                        if(notes!=null&&notes.length()>0){out.append("Editorial notes:\n");for(int n=0;n<notes.length();n++){org.json.JSONObject note=notes.getJSONObject(n);out.append("- ").append(note.optString("text")).append("\n");}out.append("\n");}
                        org.json.JSONArray refs=record.optJSONArray("cross_references");
                        if(refs!=null&&refs.length()>0){out.append("Cross-references:\n");for(int n=0;n<refs.length();n++){org.json.JSONObject ref=refs.getJSONObject(n);out.append("- ").append(ref.optString("text")).append(" ").append(ref.optString("corresp")).append("\n");}out.append("\n");}
                        count++;
                    }
                    reader.close();
                }catch(Exception e){return "Unable to read the offline Ignatius Greek text: "+e.getMessage();}
                return count==0?"No sections were found for this letter and chapter.":count+" sections\n\n"+out.toString()+"\nNo missing wording is reconstructed.";
            }
            protected void onPostExecute(String result){
                TextView view=text(result,15,ink,false);enablePassageSelection(view);
                ScrollView sv=new ScrollView(MainActivity.this);sv.setPadding(12,8,12,8);sv.addView(view);
                new android.app.AlertDialog.Builder(MainActivity.this).setTitle("Ignatius · "+chapter).setView(sv)
                    .setNegativeButton("Back to chapters",(d,w)->openIgnatiusLetter(letterNo)).setPositiveButton("Close",null).show();
            }
        }.executeOnExecutor(android.os.AsyncTask.THREAD_POOL_EXECUTOR);
    }

    void openOdesOfSolomonArchive(){
        try{
            java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("other_reference/odes_of_solomon/odes_syriac_index.json"),"UTF-8"));
            StringBuilder raw=new StringBuilder();String line;while((line=reader.readLine())!=null)raw.append(line);reader.close();
            org.json.JSONArray odes=new org.json.JSONObject(raw.toString()).getJSONArray("odes");String[] nums=new String[odes.length()];String[] labels=new String[odes.length()];
            for(int i=0;i<odes.length();i++){org.json.JSONObject ode=odes.getJSONObject(i);nums[i]=ode.optString("ode");labels[i]="Ode "+nums[i]+" · "+ode.optInt("stanza_count")+" stanzas";}
            new android.app.AlertDialog.Builder(this).setTitle("Odes of Solomon · Syriac text (Odes 3–42)")
                .setItems(labels,(d,w)->openOdesOfSolomonOde(nums[w])).setNegativeButton("Close",null).show();
        }catch(Exception e){showInfo("Odes of Solomon unavailable","The offline Syriac text was not generated in this build. "+e.getMessage());}
    }
    void openOdesOfSolomonOde(String ode){
        new android.os.AsyncTask<Void,Void,String>(){
            protected String doInBackground(Void... ignored){
                StringBuilder out=new StringBuilder();int count=0;String lastStanza="";
                try{
                    java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("other_reference/odes_of_solomon/odes_syriac.jsonl"),"UTF-8"),8192);
                    String raw;while((raw=reader.readLine())!=null){
                        org.json.JSONObject record=new org.json.JSONObject(raw);if(!ode.equals(record.optString("ode")))continue;
                        if(count==0)out.append("Language: Classical Syriac\n")
                            .append("Source: Digital Syriac Corpus; Charlesworth (1973)\n")
                            .append("Transcription: Michael Oez; TEI encoding: James E. Walters\n")
                            .append("Licence: CC BY 4.0 for the TEI edition; Syriac base text public domain\n")
                            .append("Source status: UncorrectedTranscription; print transcription, not a fresh manuscript transcription. Only Odes 3–42 are included.\n\n");
                        String stanza=record.optString("stanza");
                        if(!stanza.equals(lastStanza)){out.append("Stanza ").append(stanza).append("\n");lastStanza=stanza;}
                        out.append(record.optString("text")).append("\n");count++;
                    }reader.close();return count==0?"No Syriac text records found for this ode.":count+" Syriac lines\n\n"+out.toString();
                }catch(Exception e){return "Unable to read the offline Syriac text: "+e.getMessage();}
            }
            protected void onPostExecute(String result){
                TextView view=text(result,16,ink,false);enablePassageSelection(view);
                ScrollView sv=new ScrollView(MainActivity.this);sv.setPadding(12,8,12,8);sv.addView(view);
                new android.app.AlertDialog.Builder(MainActivity.this).setTitle("Ode "+ode+" · Syriac").setView(sv)
                    .setNegativeButton("Back to Odes",(d,w)->openOdesOfSolomonArchive()).setPositiveButton("Close",null).show();
            }
        }.executeOnExecutor(android.os.AsyncTask.THREAD_POOL_EXECUTOR);
    }

    void openThreeBaruchArchive(){
        try{
            java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("other_reference/3_baruch/3bar_greek_index.json"),"UTF-8"));
            StringBuilder raw=new StringBuilder();String line;while((line=reader.readLine())!=null)raw.append(line);reader.close();
            org.json.JSONObject index=new org.json.JSONObject(raw.toString());org.json.JSONArray chapters=index.getJSONArray("chapters");
            String[] nums=new String[chapters.length()];String[] labels=new String[chapters.length()];
            for(int i=0;i<chapters.length();i++){nums[i]=chapters.getString(i);labels[i]=nums[i].equals("Prologue")?"Prologue":"Chapter "+nums[i];}
            new android.app.AlertDialog.Builder(this).setTitle("3 Baruch · Greek critical edition").setItems(labels,(d,w)->openThreeBaruchChapter(nums[w])).setNegativeButton("Close",null).show();
        }catch(Exception e){showInfo("3 Baruch Greek text unavailable","The offline Greek text was not generated in this build. "+e.getMessage());}
    }
    void openThreeBaruchChapter(String chapter){
        new android.os.AsyncTask<Void,Void,String>(){
            protected String doInBackground(Void... ignored){
                StringBuilder out=new StringBuilder();int count=0;
                try{
                    java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("other_reference/3_baruch/3bar_greek.jsonl"),"UTF-8"),8192);
                    String raw;while((raw=reader.readLine())!=null){
                        org.json.JSONObject record=new org.json.JSONObject(raw);if(!chapter.equals(record.optString("chapter")))continue;
                        if(count==0)out.append("Source: J.-C. Picard, Apocalypsis Baruchi Graece (1967), as encoded in OCP TEI\n")
                            .append("Language: Ancient Greek\nLicence: CC BY 4.0\n")
                            .append("TEI editors: Ken M. Penner and David M. Miller\n")
                            .append("Edition-derived Greek critical text, not a fresh diplomatic transcription. Slavonic tradition is not included.\n\n");
                        out.append(record.optString("reference")).append("\n").append(record.optString("text")).append("\n\n");count++;
                    }reader.close();return count==0?"No Greek text records found for this division.":count+" Greek text records\n\n"+out.toString();
                }catch(Exception e){return "Unable to read the offline Greek text: "+e.getMessage();}
            }
            protected void onPostExecute(String result){
                TextView view=text(result,15,ink,false);enablePassageSelection(view);
                ScrollView sv=new ScrollView(MainActivity.this);sv.setPadding(12,8,12,8);sv.addView(view);
                new android.app.AlertDialog.Builder(MainActivity.this).setTitle("3 Baruch · "+chapter).setView(sv)
                    .setNegativeButton("Back to chapters",(d,w)->openThreeBaruchArchive()).setPositiveButton("Close",null).show();
            }
        }.executeOnExecutor(android.os.AsyncTask.THREAD_POOL_EXECUTOR);
    }

    void openTwoBaruchArchive(){
        try{
            java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("other_reference/2_baruch/2_baruch_index.json"),"UTF-8"));
            StringBuilder raw=new StringBuilder();String line;while((line=reader.readLine())!=null)raw.append(line);reader.close();
            org.json.JSONArray witnesses=new org.json.JSONObject(raw.toString()).getJSONArray("witnesses");
            String[] labels=new String[witnesses.length()];String[] ids=new String[witnesses.length()];
            for(int i=0;i<witnesses.length();i++){org.json.JSONObject w=witnesses.getJSONObject(i);ids[i]=w.optString("witness");labels[i]=w.optString("title")+" · "+w.optInt("chapter_count")+" chapters";}
            new android.app.AlertDialog.Builder(this).setTitle("2 Baruch · Syriac witnesses")
                .setItems(labels,(d,w)->openTwoBaruchWitness(ids[w]))
                .setNegativeButton("Close",null).show();
        }catch(Exception e){showInfo("2 Baruch unavailable","The offline Syriac text was not generated in this build. "+e.getMessage());}
    }

    void openTwoBaruchWitness(String witness){
        try{
            java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("other_reference/2_baruch/2_baruch_index.json"),"UTF-8"));
            StringBuilder raw=new StringBuilder();String line;while((line=reader.readLine())!=null)raw.append(line);reader.close();
            org.json.JSONArray groups=new org.json.JSONObject(raw.toString()).getJSONArray("witnesses");
            org.json.JSONObject selected=null;for(int i=0;i<groups.length();i++)if(witness.equals(groups.getJSONObject(i).optString("witness")))selected=groups.getJSONObject(i);
            if(selected==null)return;
            org.json.JSONArray chapters=selected.getJSONArray("chapters");int[] nums=new int[chapters.length()];String[] labels=new String[chapters.length()];
            for(int i=0;i<chapters.length();i++){nums[i]=chapters.getInt(i);labels[i]="Chapter "+nums[i];}
            new android.app.AlertDialog.Builder(this).setTitle(selected.optString("title"))
                .setItems(labels,(d,w)->openTwoBaruchChapter(witness,nums[w]))
                .setNegativeButton("Back to witnesses",(d,w)->openTwoBaruchArchive()).show();
        }catch(Exception e){showInfo("2 Baruch index unavailable",e.getMessage());}
    }

    void openTwoBaruchChapter(String witness,int chapter){
        new android.os.AsyncTask<Void,Void,String>(){
            protected String doInBackground(Void... ignored){
                StringBuilder out=new StringBuilder();int count=0;
                try{
                    java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("other_reference/2_baruch/2_baruch_syriac.jsonl"),"UTF-8"),8192);
                    String raw;while((raw=reader.readLine())!=null){
                        org.json.JSONObject record=new org.json.JSONObject(raw);
                        if(!witness.equals(record.optString("witness"))||record.optInt("chapter")!=chapter)continue;
                        if(count==0)out.append("Source: ETCBC electronic Peshitta, version 0.2\n")
                            .append("Language: Classical Syriac\nLicence: CC BY-NC 4.0; non-commercial use only\n")
                            .append("Text basis: OCR-derived from the printed Vetus Testamentum Syriace edition; critical apparatus omitted.\n")
                            .append("This is not a fresh diplomatic transcription of Codex Ambrosianus. The two Epistle forms remain separate.\n\n");
                        out.append(record.optString("reference")).append("\n").append(record.optString("text")).append("\n\n");count++;
                    }reader.close();
                    return count==0?"No Syriac records found for this chapter.":count+" numbered text records\n\n"+out.toString();
                }catch(Exception e){return "Unable to read the offline Syriac text: "+e.getMessage();}
            }
            protected void onPostExecute(String result){
                TextView view=text(result,15,ink,false);enablePassageSelection(view);
                ScrollView sv=new ScrollView(MainActivity.this);sv.setPadding(12,8,12,8);sv.addView(view);
                new android.app.AlertDialog.Builder(MainActivity.this).setTitle("2 Baruch · Chapter "+chapter)
                    .setView(sv).setNegativeButton("Back to chapters",(d,w)->openTwoBaruchWitness(witness))
                    .setPositiveButton("Close",null).show();
            }
        }.executeOnExecutor(android.os.AsyncTask.THREAD_POOL_EXECUTOR);
    }

    void openAscensionIsaiahArchive(){
        try{
            java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("other_reference/ascension_isaiah/ascension_isaiah_index.json"),"UTF-8"));
            StringBuilder raw=new StringBuilder();String line;while((line=reader.readLine())!=null)raw.append(line);reader.close();
            org.json.JSONObject index=new org.json.JSONObject(raw.toString());
            org.json.JSONArray sections=index.getJSONArray("sections");
            int[] numbers=new int[sections.length()];String[] labels=new String[sections.length()];
            for(int i=0;i<sections.length();i++){numbers[i]=sections.getInt(i);labels[i]="Section "+numbers[i];}
            new android.app.AlertDialog.Builder(this).setTitle("Ascension of Isaiah · Ge'ez")
                .setItems(labels,(dialog,which)->openAscensionIsaiahSection(numbers[which]))
                .setNegativeButton("Close",null).show();
        }catch(Exception e){showInfo("Ge'ez text unavailable","The offline Ascension of Isaiah text was not generated in this build. "+e.getMessage());}
    }

    void openAscensionIsaiahSection(int section){
        new android.os.AsyncTask<Void,Void,String>(){
            protected String doInBackground(Void... ignored){
                StringBuilder out=new StringBuilder();int count=0;
                try{
                    java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("other_reference/ascension_isaiah/ascension_isaiah_geez.jsonl"),"UTF-8"),8192);
                    String raw;
                    while((raw=reader.readLine())!=null){
                        org.json.JSONObject record=new org.json.JSONObject(raw);
                        if(record.optInt("section")!=section)continue;
                        if(count==0)out.append("Work: Ascension of Isaiah\nLanguage: Classical Ethiopic (Ge'ez)\n")
                            .append("Edition basis: Library of Ethiopic Texts transcription (1995)\n")
                            .append("TEI encoding: Beta maṣāḥǝft, Universität Hamburg\n")
                            .append("Reuse: non-commercial use only for the underlying Ge'ez text\n")
                            .append("This is an edition-based Unicode transcription, not a fresh diplomatic transcription of one manuscript. The pinned source file contains only five numbered sections and is not a complete transcription of the work. The Ge'ez tradition represents a translation from a lost Greek textual form. Other language witnesses are separate.\n\n");
                        out.append(record.optString("reference")).append("\n\n").append(record.optString("text")).append("\n\n");
                        count++;
                    }
                    reader.close();
                    return count==0?"No Ge'ez text records found for section "+section+".":out.toString();
                }catch(Exception e){return "Unable to read the offline Ge'ez text: "+e.getMessage();}
            }
            protected void onPostExecute(String result){
                TextView view=text(result,15,ink,false);enablePassageSelection(view);
                ScrollView sv=new ScrollView(MainActivity.this);sv.setPadding(12,8,12,8);sv.addView(view);
                new android.app.AlertDialog.Builder(MainActivity.this).setTitle("Ascension of Isaiah · section "+section)
                    .setView(sv).setNegativeButton("Back to sections",(d,w)->openAscensionIsaiahArchive())
                    .setPositiveButton("Close",null).show();
            }
        }.executeOnExecutor(android.os.AsyncTask.THREAD_POOL_EXECUTOR);
    }

    void openGreekEnochArchive(){
        try{
            java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("other_reference/enoch_greek/enoch_greek_index.json"),"UTF-8"));
            StringBuilder raw=new StringBuilder();String line;while((line=reader.readLine())!=null)raw.append(line);reader.close();
            org.json.JSONObject index=new org.json.JSONObject(raw.toString());
            org.json.JSONArray pages=index.getJSONArray("printed_pages");
            int[] numbers=new int[pages.length()];String[] labels=new String[pages.length()];
            for(int i=0;i<pages.length();i++){numbers[i]=pages.getInt(i);labels[i]="Printed edition page "+numbers[i];}
            new android.app.AlertDialog.Builder(this).setTitle("1 Enoch · Greek edition fragments")
                .setItems(labels,(dialog,which)->openGreekEnochPage(numbers[which]))
                .setNegativeButton("Close",null).show();
        }catch(Exception e){
            showInfo("Greek Enoch text unavailable","The offline Greek edition text was not generated in this build. "+e.getMessage());
        }
    }

    void openGreekEnochPage(int page){
        new android.os.AsyncTask<Void,Void,String>(){
            protected String doInBackground(Void... ignored){
                StringBuilder out=new StringBuilder();int count=0;
                try{
                    java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("other_reference/enoch_greek/enoch_greek.jsonl"),"UTF-8"),8192);
                    String raw;
                    while((raw=reader.readLine())!=null){
                        org.json.JSONObject record=new org.json.JSONObject(raw);
                        if(record.optInt("printed_page")!=page)continue;
                        if(count==0)out.append("Work: 1 Enoch\nLanguage: Ancient Greek\n")
                            .append("Edition: Johannes Flemming, Das Buch Henoch (1901)\n")
                            .append("Digital source: Open Greek and Latin / First1KGreek\nLicence: CC BY-SA 4.0\n")
                            .append("This is fragmentary, edition-derived Greek text, not a complete manuscript or a diplomatic transcription of one codex. Aramaic and Ethiopic witnesses remain separate. No missing wording is reconstructed.\n\n");
                        out.append(record.optString("reference")).append(" · printed page ").append(page).append("\n")
                            .append(record.optString("text")).append("\n\n");
                        count++;
                    }
                    reader.close();
                    return count==0?"No Greek text records were found for printed page "+page+".":count+" Greek text paragraphs\n\n"+out.toString();
                }catch(Exception e){return "Unable to read the offline Greek Enoch text: "+e.getMessage();}
            }
            protected void onPostExecute(String result){
                TextView view=text(result,15,ink,false);enablePassageSelection(view);
                ScrollView sv=new ScrollView(MainActivity.this);sv.setPadding(12,8,12,8);sv.addView(view);
                new android.app.AlertDialog.Builder(MainActivity.this).setTitle("1 Enoch · Greek page "+page)
                    .setView(sv).setNegativeButton("Back to page index",(d,w)->openGreekEnochArchive())
                    .setPositiveButton("Close",null).show();
            }
        }.executeOnExecutor(android.os.AsyncTask.THREAD_POOL_EXECUTOR);
    }

    void openEnochWitnessMenu(){
        String[] choices={"Complete Ge'ez edition · 108 chapters","Greek edition fragments"};
        new android.app.AlertDialog.Builder(this).setTitle("1 Enoch · Other language witnesses")
            .setItems(choices,(dialog,which)->{if(which==0)openEnochGeezArchive();else openGreekEnochArchive();})
            .setNegativeButton("Close",null).show();
    }

    void openEnochGeezArchive(){
        try{
            java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("other_reference/enoch_geez/enoch_geez_index.json"),"UTF-8"));
            StringBuilder raw=new StringBuilder();String line;while((line=reader.readLine())!=null)raw.append(line);reader.close();
            org.json.JSONObject index=new org.json.JSONObject(raw.toString());
            org.json.JSONArray chapters=index.getJSONArray("chapters");
            String[] labels=new String[chapters.length()];int[] numbers=new int[chapters.length()];
            for(int i=0;i<chapters.length();i++){numbers[i]=chapters.getInt(i);labels[i]="Chapter "+numbers[i];}
            new android.app.AlertDialog.Builder(this).setTitle("1 Enoch · Ge'ez EOTC edition")
                .setItems(labels,(dialog,which)->openEnochGeezChapter(numbers[which]))
                .setNegativeButton("Back to witnesses",(dialog,which)->openEnochWitnessMenu()).show();
        }catch(Exception e){showInfo("Ge'ez Enoch text unavailable","The offline EOTC Ge'ez edition was not generated in this build. "+e.getMessage());}
    }

    void openEnochGeezChapter(int chapter){
        new android.os.AsyncTask<Void,Void,String>(){
            protected String doInBackground(Void... ignored){
                StringBuilder out=new StringBuilder();int count=0;
                try{
                    java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("other_reference/enoch_geez/enoch_geez.jsonl"),"UTF-8"),8192);
                    String raw;while((raw=reader.readLine())!=null){
                        org.json.JSONObject record=new org.json.JSONObject(raw);
                        if(record.optInt("chapter")!=chapter)continue;
                        if(count==0)out.append("Work: 1 Enoch\nLanguage: Classical Ethiopic (Ge'ez)\n")
                            .append("Edition: Ethiopian Orthodox Tewahedo Church printed edition (EOTCed)\n")
                            .append("Source: Beta maṣāḥǝft, LIT1340EnochE.xml\nLicence: CC BY-SA 4.0\n")
                            .append("This is a complete edition-based Ge'ez text, not a fresh diplomatic transcription of one named ancient codex. The separate Dillmann/Jerabek edition division is excluded because it carries a distinct non-commercial permission notice. Qumran Aramaic fragments and Greek fragments remain separate witnesses; Ge'ez does not restore Hebrew or Aramaic wording.\n\n");
                        out.append(record.optString("reference")).append("\n").append(record.optString("text")).append("\n\n");count++;
                    }
                    reader.close();
                    return count==0?"No Ge'ez text records found for 1 Enoch chapter "+chapter+".":count+" numbered text records\n\n"+out.toString();
                }catch(Exception e){return "Unable to read the offline Ge'ez Enoch text: "+e.getMessage();}
            }
            protected void onPostExecute(String result){
                TextView view=text(result,15,ink,false);enablePassageSelection(view);
                ScrollView sv=new ScrollView(MainActivity.this);sv.setPadding(12,8,12,8);sv.addView(view);
                new android.app.AlertDialog.Builder(MainActivity.this).setTitle("1 Enoch · Ge'ez Chapter "+chapter)
                    .setView(sv).setNegativeButton("Back to chapters",(d,w)->openEnochGeezArchive()).setPositiveButton("Close",null).show();
            }
        }.executeOnExecutor(android.os.AsyncTask.THREAD_POOL_EXECUTOR);
    }

    void openQumranReferenceFragments(String title,String[] requestedIds){
        try{
            java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("dss/etcbc_scroll_index.json"),"UTF-8"));
            StringBuilder raw=new StringBuilder();String line;while((line=reader.readLine())!=null)raw.append(line);reader.close();
            org.json.JSONArray scrolls=new org.json.JSONObject(raw.toString()).getJSONArray("scrolls");
            java.util.ArrayList<String> availableIds=new java.util.ArrayList<>();
            java.util.ArrayList<String> labels=new java.util.ArrayList<>();
            for(String requested:requestedIds){
                for(int i=0;i<scrolls.length();i++){
                    org.json.JSONObject scroll=scrolls.getJSONObject(i);
                    if(requested.equals(scroll.optString("scroll"))&&scroll.optInt("line_count")>0){
                        availableIds.add(requested);
                        labels.add(requested+"  ·  "+scroll.optInt("fragment_count")+" fragments, "+scroll.optInt("line_count")+" lines");
                        break;
                    }
                }
            }
            if(availableIds.isEmpty()){
                showInfo(title+" fragments unavailable","No matching line-level Qumran transcriptions were found in the offline archive.");
                return;
            }
            String[] ids=availableIds.toArray(new String[0]);
            String[] items=labels.toArray(new String[0]);
            new android.app.AlertDialog.Builder(this).setTitle(title+" · Surviving Qumran fragments")
                .setItems(items,(dialog,which)->openEtcbcDssScroll(ids[which]))
                .setNegativeButton("Close",null).show();
        }catch(Exception e){
            showInfo(title+" fragments unavailable","Unable to open the offline Qumran witness index. "+e.getMessage());
        }
    }

    void openTestamentAbrahamArchive(){
        try{
            java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("other_reference/testament_abraham/testament_abraham_index.json"),"UTF-8"));
            StringBuilder raw=new StringBuilder();String line;while((line=reader.readLine())!=null)raw.append(line);reader.close();
            org.json.JSONArray recensions=new org.json.JSONObject(raw.toString()).getJSONArray("recensions");
            String[] ids=new String[recensions.length()];
            String[] labels=new String[recensions.length()];
            for(int i=0;i<recensions.length();i++){
                org.json.JSONObject rec=recensions.getJSONObject(i);
                ids[i]=rec.optString("recension");
                labels[i]="Recension "+ids[i]+"  ·  "+rec.optInt("chapter_count")+" chapters";
            }
            new android.app.AlertDialog.Builder(this).setTitle("Testament of Abraham · Greek recensions")
                .setItems(labels,(dialog,which)->openTestamentAbrahamRecension(ids[which]))
                .setNegativeButton("Close",null).show();
        }catch(Exception e){
            showInfo("Testament of Abraham unavailable","The offline Greek recensions were not generated in this build. "+e.getMessage());
        }
    }

    void openTestamentAbrahamRecension(String recension){
        try{
            java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("other_reference/testament_abraham/testament_abraham_index.json"),"UTF-8"));
            StringBuilder raw=new StringBuilder();String line;while((line=reader.readLine())!=null)raw.append(line);reader.close();
            org.json.JSONArray recensions=new org.json.JSONObject(raw.toString()).getJSONArray("recensions");
            org.json.JSONObject selected=null;
            for(int i=0;i<recensions.length();i++){org.json.JSONObject item=recensions.getJSONObject(i);if(recension.equals(item.optString("recension"))){selected=item;break;}}
            if(selected==null)throw new Exception("The requested recension is not indexed.");
            org.json.JSONArray chapters=selected.getJSONArray("chapters");
            String assetFile=selected.optString("asset_file");
            int[] numbers=new int[chapters.length()];
            String[] labels=new String[chapters.length()];
            for(int i=0;i<chapters.length();i++){numbers[i]=chapters.optInt(i);labels[i]="Chapter "+numbers[i];}
            new android.app.AlertDialog.Builder(this).setTitle("Recension "+recension+" · Chapters")
                .setItems(labels,(dialog,which)->openTestamentAbrahamChapter(recension,numbers[which],assetFile))
                .setNegativeButton("Back to recensions",(d,w)->openTestamentAbrahamArchive()).show();
        }catch(Exception e){
            showInfo("Recension unavailable","Unable to open the chapter index. "+e.getMessage());
        }
    }

    void openTestamentAbrahamChapter(String recension,int chapter,String assetFile){
        new android.os.AsyncTask<Void,Void,String>(){
            protected String doInBackground(Void... ignored){
                StringBuilder out=new StringBuilder();int count=0;
                try{
                    java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open(assetFile),"UTF-8"),8192);
                    String raw;
                    while((raw=reader.readLine())!=null){
                        org.json.JSONObject record=new org.json.JSONObject(raw);
                        if(record.optInt("chapter")!=chapter)continue;
                        if(count==0)out.append("Source: M. R. James, Testament of Abraham, Recension "+recension+"\n")
                            .append("Digital edition: Open Greek and Latin / First1KGreek\n")
                            .append("Licence: CC BY-SA 4.0\n")
                            .append("Textual basis: printed Greek edition based on manuscript tradition; not a direct diplomatic transcription of one codex\n")
                            .append("Recensions A and B are kept separate. No missing wording is reconstructed.\n\n");
                        out.append(record.optString("reference")).append("\n");
                        org.json.JSONArray pages=record.optJSONArray("source_pages");
                        if(pages!=null&&pages.length()>0)out.append("Printed page marker(s): ").append(pages.toString()).append("\n");
                        org.json.JSONArray lines=record.optJSONArray("line_markers");
                        if(lines!=null&&lines.length()>0)out.append("Line markers: ").append(lines.toString()).append("\n");
                        out.append(record.optString("text")).append("\n");
                        org.json.JSONArray notes=record.optJSONArray("editorial_notes_and_variants");
                        if(notes!=null&&notes.length()>0){
                            out.append("Manuscript variants / editorial notes:\n");
                            for(int i=0;i<notes.length();i++){
                                org.json.JSONObject note=notes.getJSONObject(i);
                                out.append(note.optString("type")).append(" ").append(note.optString("number")).append(": ").append(note.optString("text")).append("\n");
                            }
                        }
                        out.append("\n");count++;
                    }
                    reader.close();
                    return count==0?"No source text was found for Recension "+recension+", chapter "+chapter+".":out.toString();
                }catch(Exception e){return "Unable to read Testament of Abraham: "+e.getMessage();}
            }
            protected void onPostExecute(String result){
                TextView view=text(result,15,ink,false);enablePassageSelection(view);
                ScrollView sv=new ScrollView(MainActivity.this);sv.setPadding(12,8,12,8);sv.addView(view);
                new android.app.AlertDialog.Builder(MainActivity.this).setTitle("Recension "+recension+" · Chapter "+chapter)
                    .setView(sv).setNegativeButton("Back to chapters",(d,w)->openTestamentAbrahamRecension(recension))
                    .setPositiveButton("Close",null).show();
            }
        }.executeOnExecutor(android.os.AsyncTask.THREAD_POOL_EXECUTOR);
    }

    void openHistoricalWritingEntry(String title){
        try{
            java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("catalog/historical_writings_catalog.json"),"UTF-8"));
            StringBuilder raw=new StringBuilder();String line;while((line=reader.readLine())!=null)raw.append(line);reader.close();
            org.json.JSONArray records=new org.json.JSONObject(raw.toString()).getJSONArray("records");
            org.json.JSONObject selected=null;
            for(int i=0;i<records.length();i++){org.json.JSONObject record=records.getJSONObject(i);if(title.equals(record.optString("title"))){selected=record;break;}}
            if(selected==null){showInfo("Catalogue record unavailable","No structured source record is available for this title.");return;}
            StringBuilder detail=new StringBuilder();
            detail.append("Category: ").append(selected.optString("category")).append("\n");
            detail.append("Ancient reference: ").append(selected.optString("reference","Not asserted")).append("\n");
            detail.append("Preservation: ").append(selected.optString("preservation")).append("\n");
            detail.append("Date: ").append(selected.optString("date")).append("\n");
            org.json.JSONArray languages=selected.optJSONArray("languages");
            if(languages!=null)detail.append("Languages: ").append(joinHistoricalJson(languages)).append("\n");
            org.json.JSONArray witnesses=selected.optJSONArray("witnesses");
            detail.append("\nManuscript witnesses:\n");
            if(witnesses==null||witnesses.length()==0)detail.append("No independently identified witness is currently recorded.\n");
            else for(int i=0;i<witnesses.length();i++)detail.append("- ").append(witnesses.optString(i)).append("\n");
            detail.append("\nText availability in this app:\n").append(selected.optString("text_status"));
            detail.append("\n\nResearch note:\n").append(selected.optString("note"));
            TextView view=text(detail.toString(),14,ink,false);enablePassageSelection(view);
            ScrollView scroll=new ScrollView(this);scroll.setPadding(12,8,12,8);scroll.addView(view);
            new android.app.AlertDialog.Builder(this).setTitle(title).setView(scroll).setPositiveButton("Close",null).show();
        }catch(Exception e){showInfo("Catalogue unavailable","Unable to read the historical writings catalogue: "+e.getMessage());}
    }
    String joinHistoricalJson(org.json.JSONArray values){
        ArrayList<String> items=new ArrayList<>();for(int i=0;i<values.length();i++)items.add(values.optString(i));return android.text.TextUtils.join("; ",items);
    }

    void openOtherReferenceBookEntry(String item){
        String category="Ancient reference writing";
        String preservation="Catalogue entry only; manuscript witnesses and text editions must be verified before a transcription is added.";
        String witnesses="No single manuscript witness is asserted by this catalogue entry.";
        if(item.equals("1 Enoch")){category="Jewish apocalyptic collection";preservation="Substantially preserved in Ge'ez (Ethiopic); Aramaic fragments survive among the Dead Sea Scrolls, with Greek fragments also known.";witnesses="Ge'ez manuscripts; Qumran Aramaic fragments; Greek fragments.";}
        else if(item.equals("Jubilees")){category="Jewish rewritten-Scripture work";preservation="Substantially preserved in Ge'ez; Hebrew fragments survive among the Dead Sea Scrolls.";witnesses="Ge'ez manuscripts and Qumran Hebrew fragments.";}
        else if(item.equals("Didache")){category="Early Christian church-order writing";preservation="Survives in Greek manuscript transmission and ancient versions.";witnesses="Greek Codex Hierosolymitanus 54 and other versional witnesses.";}
        else if(item.equals("Letters of Ignatius of Antioch")){category="Early Christian letters";preservation="Seven letters are preserved in multiple manuscript recensions and ancient versions.";witnesses="Greek manuscript tradition, including witnesses to the middle recension; this offline text follows Lake’s 1912 printed Greek edition."; }
        else if(item.equals("Shepherd of Hermas")){category="Early Christian visionary writing";preservation="Survives in Greek manuscripts and ancient translations, including early papyrus evidence.";witnesses="Greek codices and papyri; Latin and other versions.";}
        else if(item.equals("Gospel of Thomas")){category="Sayings gospel";preservation="Substantially preserved in Coptic, with Greek fragments.";witnesses="Nag Hammadi Codex II, 2; P.Oxy. 1, 654 and 655.";}
        else if(item.equals("Protoevangelium of James (Nativity and Infancy of Jesus)")){category="Nativity narrative";preservation="Survives in numerous Greek manuscripts and ancient translations. It narrates Mary's background and the birth of Lord Jesus; it is not a contemporary birth record.";witnesses="Greek manuscript tradition and ancient translations; also called the Infancy Gospel of James.";}
        else if(item.equals("Infancy Gospel of Thomas")){category="Childhood stories about Jesus";preservation="Survives in multiple Greek and versional forms with substantial textual variation.";witnesses="Greek manuscripts and ancient translations; recensions must be kept distinct.";}
        else if(item.equals("Gospel of Pseudo-Matthew")){category="Nativity and infancy narrative";preservation="A later Latin infancy narrative preserved in medieval manuscripts; it reworks earlier traditions.";witnesses="Latin manuscript tradition.";}
        else if(item.equals("Arabic Infancy Gospel")){category="Nativity and infancy narrative";preservation="A later collection of infancy traditions surviving in Arabic manuscripts and related versions.";witnesses="Arabic manuscript tradition; textual forms vary.";}
        else if(item.equals("Gospel of Peter")){category="Passion and resurrection narrative";preservation="Survives fragmentarily, with additional small papyrus fragments and indirect references.";witnesses="Akhmim fragment and other fragmentary witnesses.";}
        else if(item.equals("Gospel of Mary")){category="Dialogue gospel";preservation="Survives incompletely in Coptic and Greek fragments.";witnesses="Berlin Codex 8502 and Greek papyrus fragments.";}
        else if(item.equals("Gospel of Philip")){category="Early Christian sayings and sacramental discourse";preservation="Survives in a Coptic manuscript copy.";witnesses="Nag Hammadi Codex II, 3.";}
        else if(item.equals("Gospel of Truth")){category="Early Christian homiletic writing";preservation="Survives in Coptic manuscript copies.";witnesses="Nag Hammadi Codices I and XII.";}
        else if(item.equals("Gospel of Judas")){category="Dialogue gospel";preservation="Survives in a Coptic manuscript copy.";witnesses="Codex Tchacos.";}
        else if(item.equals("Acts of Peter")){category="Apocryphal acts";preservation="Survives in fragmentary Greek and Latin forms and later versions.";witnesses="Greek and Latin fragments and related recensions.";}
        else if(item.equals("Acts of Paul")){category="Apocryphal acts";preservation="Survives in fragmentary Greek witnesses and ancient versions.";witnesses="Greek papyri, fragments and ancient versions.";}
        else if(item.equals("Acts of John")){category="Apocryphal acts";preservation="Survives in Greek manuscripts and fragments, with varied recensions.";witnesses="Greek manuscript tradition and ancient versions.";}
        else if(item.equals("Acts of Thomas")){category="Apocryphal acts";preservation="Survives in Syriac and Greek recensions.";witnesses="Syriac and Greek manuscript traditions.";}
        else if(item.equals("Apocalypse of Peter")){category="Apocalyptic writing";preservation="Survives in Greek fragments and an Ethiopic version; witnesses differ.";witnesses="Akhmim Greek fragment and Ethiopic tradition.";}
        else if(item.equals("Apocalypse of Paul")){category="Apocalyptic writing";preservation="Survives in multiple Greek and versional recensions.";witnesses="Greek and ancient-language recensions.";}
        else if(item.equals("Ascension of Isaiah")){category="Jewish-Christian apocalyptic writing";preservation="Substantially preserved in Ethiopic, with Greek, Latin and Slavonic witnesses.";witnesses="Ethiopic manuscripts and Greek, Latin and Slavonic witnesses.";}
        else if(item.equals("Testament of Abraham")){category="Testamentary narrative";preservation="Survives in differing Greek recensions and ancient translations.";witnesses="Greek Recensions A and B and versional witnesses.";}
        else if(item.equals("Testament of the Twelve Patriarchs")){category="Testamentary collection";preservation="Survives principally in Greek manuscripts, with related fragmentary Semitic-language evidence.";witnesses="Greek manuscript tradition and related fragmentary witnesses.";}
        else if(item.equals("2 Baruch")){category="Jewish apocalyptic writing";preservation="Survives principally in Syriac, with other fragmentary evidence.";witnesses="Syriac manuscript tradition and fragmentary versional evidence.";}
        else if(item.equals("3 Baruch")){category="Apocalyptic writing";preservation="Survives in Greek and Slavonic forms that differ.";witnesses="Greek and Slavonic recensions.";}
        else if(item.equals("Life of Adam and Eve")){category="Adam and Eve narrative cycle";preservation="Survives in several distinct language traditions and recensions; they are not one uniform text.";witnesses="Greek, Latin, Armenian, Georgian and Slavonic traditions.";}
        else if(item.equals("Apocalypse of Moses")){category="Adam and Eve narrative; Greek recension";preservation="A Greek-language form closely related to the Life of Adam and Eve tradition. It is not a separate, securely independent account from every other recension.";witnesses="Greek manuscript tradition; commonly treated as a Greek recension within the Adam and Eve literary cycle.";}
        else if(item.equals("Dormition of Mary (Transitus Mariae traditions)")){category="Mary's Dormition and departure traditions";preservation="A family of early Christian narratives about Mary's final days and departure. The texts survive in multiple language traditions and differing recensions, not as one uniform book.";witnesses="Greek, Syriac, Coptic, Latin and other versional traditions; individual recensions require separate identification.";}
        else if(item.equals("Six Books Dormition Apocryphon")){category="Dormition narrative";preservation="An ancient Christian Dormition narrative preserved in Syriac and related traditions. Its relationship to other Transitus Mariae texts must be tracked by recension.";witnesses="Syriac manuscript tradition and related versions.";}
        else if(item.equals("Book of Mary's Repose")){category="Dormition narrative";preservation="A title used for a group of traditions about Mary's repose or departure; titles and textual identities vary across manuscripts and scholarship.";witnesses="Eastern Christian manuscript traditions; exact witness identification should accompany any future transcription.";}
        else if(item.equals("Odes of Solomon")){category="Ancient hymn collection";preservation="The Syriac collection is preserved in a manuscript tradition; Greek and Coptic fragments are separate witnesses.";witnesses="Syriac manuscripts; Greek and Coptic fragments. The offline dataset contains the Syriac Odes 3–42 transcription only.";}
        else if(item.equals("Pseudo-Philo: Biblical Antiquities")){category="Jewish rewritten-Scripture history";preservation="Survives principally in Latin manuscripts; the original language and form remain debated.";witnesses="Latin manuscript tradition.";}
        else if(item.equals("Zohar")){category="Medieval Jewish mystical literature";preservation="A medieval Aramaic literary corpus associated with the Zoharic tradition, transmitted in manuscripts and printed editions; it is not an ancient Second Temple writing.";witnesses="Medieval Aramaic manuscript tradition and later printed editions. Its historical composition and attribution are subjects of scholarship.";}
        String textStatus=item.equals("Epistle of Barnabas")?"Greek text available offline from Kirsopp Lake’s 1912 printed edition, with 21 chapter divisions, 194 sections, page markers, editorial notes and cross-references. This is edition-derived, not a direct diplomatic transcription of one ancient manuscript.":item.equals("Letters of Ignatius of Antioch")?"Seven Greek letters are available offline from Kirsopp Lake’s 1912 printed edition. Chapter and section labels, source page markers, editorial notes and cross-references are retained. This is edition-derived, not a direct diplomatic transcription of one manuscript.":item.equals("Gospel of Thomas")?"Sahidic Coptic text from Nag Hammadi Codex II is available offline, indexed by manuscript page, column and line. The digital edition is based on examination of the facsimile; it is not a new independent transcription.":item.equals("Didache")?"Greek text available offline from the Lake 1912 edition, with the source page markers, notes and cross-references retained. This is an edition-derived text, not a direct manuscript transcription.":item.equals("Shepherd of Hermas")?"Greek text available offline from the Lake 1917 edition, with book/chapter/section references, page markers, notes and cross-references retained. This is an edition-derived text, not a direct manuscript transcription.":item.equals("1 Enoch")?"Aramaic Qumran fragments and a separate Greek fragment text from the Flemming 1901 edition are available offline. Neither dataset is a complete Ethiopic or Greek copy; no continuous book is reconstructed.":item.equals("Jubilees")?"Fragmentary Hebrew Qumran witness texts are available offline for the identified scrolls. These are manuscript fragments, not a complete Ethiopic text or a reconstructed continuous book.":item.equals("Testament of Abraham")?"Both Greek recensions are available offline as separate editions. Manuscript-variant notes, source page markers and editorial deletions are retained. These are edition-derived texts, not direct diplomatic transcriptions of one codex.":item.equals("Odes of Solomon")?"Syriac text for Odes 3–42 is available offline. It is the Digital Syriac Corpus print transcription based on Charlesworth (1973), marked UncorrectedTranscription; it is not a fresh diplomatic transcription. Greek and Coptic fragments remain separate, and Odes 1–2 are not reconstructed.":item.equals("Testament of the Twelve Patriarchs")?"A provisional Greek base text is available offline, organized by patriarch and chapter. The OCP source identifies its single base witness as Wikisource and explicitly says it has not yet been collated against Charles (1908); it is not a diplomatic transcription of a named ancient codex.":item.equals("Ascension of Isaiah")?"Ge'ez edition text is available offline by numbered section. The source is a Unicode transcription, not a new diplomatic transcription of one manuscript; its underlying text is licensed for non-commercial use only.":"Catalogue record only unless a separately identified transcription is available. No complete text is claimed by this entry.";
        String detail=category+"\n\nPreservation: "+preservation+"\n\nKnown witnesses: "+witnesses+"\n\nText status in this app: "+textStatus+" Different languages and recensions remain separate. This archive is for reference and historical study; inclusion here does not automatically make a work part of the Scripture collections.";
        android.app.AlertDialog.Builder builder=new android.app.AlertDialog.Builder(this).setTitle(item).setMessage(detail).setPositiveButton("Close",null);
        if(item.equals("Gospel of Thomas"))builder.setNeutralButton("Open Coptic text",(d,w)->openThomasArchive());
        if(item.equals("Didache"))builder.setNeutralButton("Open Greek text",(d,w)->openDidacheArchive());
        if(item.equals("Epistle of Barnabas"))builder.setNeutralButton("Open Greek text",(d,w)->openBarnabasArchive());
        if(item.equals("Letters of Ignatius of Antioch"))builder.setNeutralButton("Open Greek text",(d,w)->openIgnatiusArchive());
        if(item.equals("2 Baruch"))builder.setNeutralButton("Open Syriac text",(d,w)->openTwoBaruchArchive());
        if(item.equals("3 Baruch"))builder.setNeutralButton("Open Greek text",(d,w)->openThreeBaruchArchive());
        if(item.equals("Odes of Solomon"))builder.setNeutralButton("Open Syriac text",(d,w)->openOdesOfSolomonArchive());
        if(item.equals("Testament of the Twelve Patriarchs"))builder.setNeutralButton("Open Greek text",(d,w)->openTwelvePatriarchsArchive());
        if(item.equals("Shepherd of Hermas"))builder.setNeutralButton("Open Greek text",(d,w)->openHermasArchive());
        if(item.equals("1 Enoch"))builder.setNeutralButton("Open Aramaic fragments",(d,w)->openQumranReferenceFragments("1 Enoch",new String[]{"4Q201","4Q202","4Q204","4Q205","4Q206","4Q207","4Q208","4Q209","4Q210","4Q211","4Q212"}));
        if(item.equals("1 Enoch"))builder.setNegativeButton("Open Greek fragments",(d,w)->openGreekEnochArchive());
        if(item.equals("Jubilees"))builder.setNeutralButton("Open Hebrew fragments",(d,w)->openQumranReferenceFragments("Jubilees",new String[]{"4Q216","4Q217","4Q218","4Q219","4Q220","4Q221","4Q222","4Q223_224","4Q225"}));
        if(item.equals("Jubilees"))builder.setNegativeButton("Open Ge'ez editions",(d,w)->openJubileesGeezArchive());
        if(item.equals("Testament of Abraham"))builder.setNeutralButton("Open Greek recensions",(d,w)->openTestamentAbrahamArchive());
        if(item.equals("Ascension of Isaiah"))builder.setNeutralButton("Open Ge'ez text",(d,w)->openAscensionIsaiahArchive());
        builder.show();
    }

    void openReferencedBookEntry(String item){
        try{
            java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("catalog/lost_and_referenced_books_catalog.json"),"UTF-8"));
            StringBuilder raw=new StringBuilder();String line;
            while((line=reader.readLine())!=null)raw.append(line);
            reader.close();
            org.json.JSONArray records=new org.json.JSONObject(raw.toString()).getJSONArray("records");
            org.json.JSONObject selected=null;
            for(int i=0;i<records.length();i++){
                org.json.JSONObject record=records.getJSONObject(i);
                if(item.equalsIgnoreCase(record.optString("title"))){selected=record;break;}
            }
            if(selected==null){showInfo("Lost-book record unavailable","No verified structured record is available for "+item+".");return;}
            StringBuilder detail=new StringBuilder();
            detail.append("Preservation status\n").append(selected.optString("status","Not yet verified")).append("\n\n");
            detail.append("Ancient references\n");
            org.json.JSONArray refs=selected.optJSONArray("references");
            if(refs!=null)for(int i=0;i<refs.length();i++)detail.append("• ").append(refs.optString(i)).append("\n");
            detail.append("\nLanguage\n").append(selected.optString("language","Unknown")).append("\n\n");
            detail.append("Date\n").append(selected.optString("date","Undetermined")).append("\n\n");
            detail.append("Surviving manuscript witnesses\n");
            org.json.JSONArray witnesses=selected.optJSONArray("witnesses");
            if(witnesses==null||witnesses.length()==0)detail.append("No independently identified surviving manuscript witness is recorded.\n");
            else for(int i=0;i<witnesses.length();i++)detail.append("• ").append(witnesses.optString(i)).append("\n");
            detail.append("\nWhat can actually be recovered\n").append(selected.optString("recoverable","No verified surviving text is recorded."));
            detail.append("\n\nResearch note\n").append(selected.optString("note",""));
            detail.append("\n\nTextual caution\n").append(selected.optString("caution","Do not reconstruct missing wording."));
            org.json.JSONArray researchSources=selected.optJSONArray("research_sources");
            if(researchSources!=null&&researchSources.length()>0){
                detail.append("\n\nResearch sources");
                for(int i=0;i<researchSources.length();i++){
                    org.json.JSONObject source=researchSources.optJSONObject(i);
                    if(source!=null)detail.append("\n").append(source.optString("title","Source")).append("\n").append(source.optString("url",""));
                }
            }
            detail.append("\n\nArchive rule\nA quotation, source notice, fragment, or later abridgment is not the complete lost work. Missing wording is never invented.");
            TextView view=text(detail.toString(),14,ink,false);enablePassageSelection(view);
            ScrollView scroll=new ScrollView(this);scroll.setPadding(12,8,12,8);scroll.addView(view);
            android.app.AlertDialog.Builder builder=new android.app.AlertDialog.Builder(this).setTitle(item).setView(scroll).setPositiveButton("Close",null);
            if("book_giants".equals(selected.optString("id")))builder.setNeutralButton("Open surviving DSS fragments",(dialog,which)->openBookOfGiantsFragments());
            builder.show();
        }catch(Exception e){showInfo("Lost-book catalogue unavailable","Unable to read the lost and referenced books catalogue: "+e.getMessage());}
    }

    void openBookOfGiantsFragments(){
        try{
            java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("dss/etcbc_scroll_index.json"),"UTF-8"));
            StringBuilder raw=new StringBuilder();String line;while((line=reader.readLine())!=null)raw.append(line);reader.close();
            org.json.JSONArray scrolls=new org.json.JSONObject(raw.toString()).getJSONArray("scrolls");
            String[] sigla={"1Q23","1Q24","2Q26","4Q203","4Q530","4Q531","4Q532","4Q533","6Q8"};
            ArrayList<String> ids=new ArrayList<>();ArrayList<String> labels=new ArrayList<>();
            for(int i=0;i<scrolls.length();i++){
                org.json.JSONObject scroll=scrolls.getJSONObject(i);String id=scroll.optString("scroll");
                for(String siglum:sigla)if(id.equalsIgnoreCase(siglum)||id.toLowerCase().startsWith(siglum.toLowerCase()+" ")){
                    ids.add(id);labels.add(id+"  ·  "+scroll.optInt("fragment_count")+" fragments · "+scroll.optInt("line_count")+" transcribed lines");break;
                }
            }
            if(ids.isEmpty()){showInfo("Book of Giants fragments","The offline transcription index does not contain a verified line transcription for the listed Book of Giants witnesses in this build. The manuscript catalogue and fragment images remain available through the source links.");return;}
            String[] choices=labels.toArray(new String[0]);
            new android.app.AlertDialog.Builder(this).setTitle("Book of Giants · DSS witnesses").setItems(choices,(dialog,which)->openEtcbcDssScroll(ids.get(which))).setNegativeButton("Close",null).show();
        }catch(Exception e){showInfo("DSS fragment index unavailable","The offline Dead Sea Scrolls transcription index could not be opened: "+e.getMessage());}
    }

    void openVaticanusArchive(){
        try{
            java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("vaticanus/vaticanus_index.json"),"UTF-8"));
            StringBuilder raw=new StringBuilder();String line;while((line=reader.readLine())!=null)raw.append(line);reader.close();
            org.json.JSONObject index=new org.json.JSONObject(raw.toString());
            org.json.JSONArray pages=index.getJSONArray("pages");
            String[] labels=new String[pages.length()];
            String[] ids=new String[pages.length()];
            for(int i=0;i<pages.length();i++){
                org.json.JSONObject page=pages.getJSONObject(i);
                ids[i]=page.optString("page_id");
                labels[i]=ids[i]+"  ·  "+page.optInt("record_count")+" text records";
            }
            new android.app.AlertDialog.Builder(this).setTitle("Codex Vaticanus · Offline Page Archive")
                .setItems(labels,(dialog,which)->openVaticanusPage(ids[which]))
                .setNegativeButton("Close",null).show();
        }catch(Exception e){
            showInfo("Vaticanus transcription unavailable","The offline Codex Vaticanus transcription was not generated in this build. "+e.getMessage());
        }
    }

    void openVaticanusPage(String pageId){
        final String selected=pageId;
        new android.os.AsyncTask<Void,Void,String>(){
            protected String doInBackground(Void... ignored){
                StringBuilder out=new StringBuilder();int count=0;
                try{
                    java.io.BufferedReader indexReader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("vaticanus/vaticanus_index.json"),"UTF-8"));
                    StringBuilder indexRaw=new StringBuilder();String indexLine;while((indexLine=indexReader.readLine())!=null)indexRaw.append(indexLine);indexReader.close();
                    org.json.JSONArray pages=new org.json.JSONObject(indexRaw.toString()).getJSONArray("pages");
                    String assetPath=null;
                    for(int i=0;i<pages.length();i++){org.json.JSONObject page=pages.getJSONObject(i);if(selected.equals(page.optString("page_id"))){assetPath=page.optString("asset_file");break;}}
                    if(assetPath==null)return "No offline page file is indexed for "+selected+".";
                    java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(new java.util.zip.GZIPInputStream(getAssets().open(assetPath)),"UTF-8"),8192);
                    String raw;
                    while((raw=reader.readLine())!=null){
                        org.json.JSONObject record=new org.json.JSONObject(raw);
                        if(count==0)out.append("Source: Codex Vaticanus (GA 03), INTF / New Testament Virtual Manuscript Room\n")
                            .append("Licence: Creative Commons Attribution 4.0 International (CC BY 4.0)\n")
                            .append("Original source labels and page/column/line identifiers are retained where present.\n")
                            .append("Original-hand readings are displayed; corrections are retained as notes. Missing portions are not supplied.\n\n");
                        if(!record.optString("source_label").isEmpty())out.append(record.optString("source_label")).append("\n");
                        out.append("Page: ").append(record.optString("page_id")).append("\n");
                        out.append("Column: ").append(record.optJSONArray("column_ids")==null?"":record.optJSONArray("column_ids").toString()).append("\n");
                        out.append("Line: ").append(record.optJSONArray("line_ids")==null?"":record.optJSONArray("line_ids").toString()).append("\n");
                        out.append(record.optString("text")).append("\n");
                        org.json.JSONArray notes=record.optJSONArray("correction_notes");
                        if(notes!=null)for(int i=0;i<notes.length();i++)out.append("Correction note: ").append(notes.optString(i)).append("\n");
                        out.append("\n");count++;
                    }
                    reader.close();
                    return count==0?"No transcription records were found for "+selected+".":count+" source text records\n\n"+out.toString();
                }catch(Exception e){return "Unable to read the offline Codex Vaticanus transcription: "+e.getMessage();}
            }
            protected void onPostExecute(String result){
                TextView view=text(result,15,ink,false);enablePassageSelection(view);
                ScrollView sv=new ScrollView(MainActivity.this);sv.setPadding(12,8,12,8);sv.addView(view);
                new android.app.AlertDialog.Builder(MainActivity.this).setTitle(selected+" · Codex Vaticanus")
                    .setView(sv).setNegativeButton("Back to page index",(d,w)->openVaticanusArchive())
                    .setPositiveButton("Close",null).show();
            }
        }.executeOnExecutor(android.os.AsyncTask.THREAD_POOL_EXECUTOR);
    }

    void openJohnWitnessComparison(){
        openJohnWitnessComparison("");
    }

    void openJohnWitnessComparison(String initialReference){
        EditText input=new EditText(this);
        input.setSingleLine(true);
        input.setHint("Chapter:verse, for example 17:11");
        input.setText(initialReference==null?"":initialReference);
        input.setTextColor(ink);
        input.setHintTextColor(muted);
        new android.app.AlertDialog.Builder(this)
            .setTitle("Compare a passage in John")
            .setView(input)
            .setNegativeButton("Cancel",null)
            .setPositiveButton("Compare",(dialog,which)->{
                java.util.regex.Matcher match=java.util.regex.Pattern.compile("^\\s*(\\d{1,2})\\s*:\\s*(\\d{1,2})\\s*$").matcher(input.getText().toString());
                if(!match.matches()){
                    showInfo("Reference required","Enter a chapter and verse, such as 17:11.");
                    return;
                }
                int chapter=Integer.parseInt(match.group(1));
                int verse=Integer.parseInt(match.group(2));
                if(chapter<1||chapter>21||verse<1||verse>60){
                    showInfo("Reference out of range","Enter a verse from John chapters 1–21.");
                    return;
                }
                showJohnWitnessVerse(chapter,verse);
            }).show();
    }

    void showJohnWitnessVerse(int chapter,int verse){
        final int selectedChapter=chapter;
        final int selectedVerse=verse;
        final String reference="John "+chapter+":"+verse;
        new android.os.AsyncTask<Void,Void,String>(){
            protected String doInBackground(Void... ignored){
                try{
                    java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("catalog/john_witness_index.json"),"UTF-8"),8192);
                    StringBuilder raw=new StringBuilder();String line;
                    while((line=reader.readLine())!=null)raw.append(line);
                    reader.close();
                    org.json.JSONObject index=new org.json.JSONObject(raw.toString());
                    org.json.JSONArray verses=index.getJSONArray("verses");
                    org.json.JSONObject selected=null;
                    for(int i=0;i<verses.length();i++){
                        org.json.JSONObject item=verses.getJSONObject(i);
                        if(selectedChapter==item.optInt("chapter")&&selectedVerse==item.optInt("verse")){selected=item;break;}
                    }
                    if(selected==null){
                        return reference+"\\n\\nNo verse-indexed transcription record was found for this reference among the imported witnesses. This does not by itself establish whether the verse was absent from a manuscript, physically lost, illegible, or omitted from the source transcription. Check the page archive and source apparatus.\\n\\n"+index.optString("absence_policy");
                    }
                    StringBuilder out=new StringBuilder();
                    out.append(reference).append("\\n\\n");
                    out.append("Diplomatic Greek transcriptions are shown separately. Brackets, spelling, and source notation are retained where supplied by the source importer.\\n\\n");
                    org.json.JSONObject witnessRecords=selected.getJSONObject("witnesses");
                    org.json.JSONObject metadata=index.getJSONObject("witness_metadata");
                    String priorityWitness=selected.optString("priority_witness","");
                    if(!priorityWitness.isEmpty()){
                        out.append("Papyrus-first reading aid\\n");
                        out.append("Selected witness: ").append(priorityWitness).append(" (").append(selected.optString("priority_status","")).append(")\\n");
                        out.append(selected.optString("priority_text","")).append("\\n");
                        org.json.JSONArray partials=selected.optJSONArray("earlier_witnesses_with_editorial_supply");
                        if(partials!=null&&partials.length()>0)out.append("Earlier witness(es) with editorial supply: ").append(partials.join(", ")).append("\\n");
                        out.append(selected.optString("priority_note","")).append("\\n\\n");
                    }
                    String[] order={"P52","P66","P75","Vaticanus","Sinaiticus"};
                    int shown=0;
                    for(String witness:order){
                        if(!witnessRecords.has(witness))continue;
                        org.json.JSONObject record=witnessRecords.getJSONObject(witness);
                        org.json.JSONObject source=metadata.optJSONObject(witness);
                        out.append(witness).append("\\n");
                        out.append(record.optString("text","[No text record]")).append("\\n");
                        if(source!=null){
                            out.append("Source: ").append(source.optString("source_url","")).append("\\n");
                            out.append("Licence: ").append(source.optString("license","")).append("\\n");
                        }
                        org.json.JSONArray pages=record.optJSONArray("pages");
                        if(pages!=null&&pages.length()>0)out.append("Page(s): ").append(pages.join(", ")).append("\\n");
                        org.json.JSONArray labels=record.optJSONArray("source_labels");
                        if(labels!=null&&labels.length()>0)out.append("Source label(s): ").append(labels.join(", ")).append("\\n");
                        org.json.JSONArray lineIds=record.optJSONArray("line_ids");
                        if(lineIds!=null&&lineIds.length()>0)out.append("Line(s): ").append(lineIds.join(", ")).append("\\n");
                        org.json.JSONArray notes=record.optJSONArray("correction_notes");
                        if(notes!=null)for(int i=0;i<notes.length();i++)out.append("Correction note: ").append(notes.optString(i)).append("\\n");
                        out.append("\\n");
                        shown++;
                    }
                    if(shown==0)out.append("No witness text is indexed for this verse.\\n");
                    out.append("Caution: a missing witness entry is not automatically a textual omission. Consult the manuscript image and the full diplomatic transcription before deciding why the text is not represented.");
                    return out.toString();
                }catch(Exception e){
                    return "Unable to open the offline John witness index: "+e.getMessage();
                }
            }
            protected void onPostExecute(String result){
                TextView view=text(result,15,ink,false);enablePassageSelection(view);
                ScrollView scroll=new ScrollView(MainActivity.this);scroll.setPadding(12,8,12,8);scroll.addView(view);
                new android.app.AlertDialog.Builder(MainActivity.this).setTitle(reference+" · Witness comparison")
                    .setView(scroll)
                    .setNegativeButton("Compare another",(dialog,which)->openJohnWitnessComparison(reference.substring(5)))
                    .setPositiveButton("Close",null).show();
            }
        }.executeOnExecutor(android.os.AsyncTask.THREAD_POOL_EXECUTOR);
    }

    void openPapyrus46Archive(){
        try{
            java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("papyri/p46/p46_index.json"),"UTF-8"));
            StringBuilder raw=new StringBuilder();String line;while((line=reader.readLine())!=null)raw.append(line);reader.close();
            org.json.JSONObject index=new org.json.JSONObject(raw.toString());
            org.json.JSONArray pages=index.getJSONArray("pages");
            String[] labels=new String[pages.length()];
            String[] ids=new String[pages.length()];
            for(int i=0;i<pages.length();i++){
                org.json.JSONObject page=pages.getJSONObject(i);
                ids[i]=page.optString("page_id");
                labels[i]=ids[i]+"  ·  "+page.optInt("record_count")+" text records";
            }
            new android.app.AlertDialog.Builder(this).setTitle("Papyrus 46 · Offline Page Archive")
                .setItems(labels,(dialog,which)->openPapyrus46Page(ids[which]))
                .setNegativeButton("Close",null).show();
        }catch(Exception e){
            showInfo("Papyrus 46 transcription unavailable","The offline P46 transcription was not generated in this build. "+e.getMessage());
        }
    }

    void openPapyrus46Page(String pageId){
        final String selected=pageId;
        new android.os.AsyncTask<Void,Void,String>(){
            protected String doInBackground(Void... ignored){
                StringBuilder out=new StringBuilder();int count=0;
                try{
                    java.io.BufferedReader indexReader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("papyri/p46/p46_index.json"),"UTF-8"));
                    StringBuilder indexRaw=new StringBuilder();String indexLine;while((indexLine=indexReader.readLine())!=null)indexRaw.append(indexLine);indexReader.close();
                    org.json.JSONArray pages=new org.json.JSONObject(indexRaw.toString()).getJSONArray("pages");
                    String assetPath=null;
                    for(int i=0;i<pages.length();i++){org.json.JSONObject page=pages.getJSONObject(i);if(selected.equals(page.optString("page_id"))){assetPath=page.optString("asset_file");break;}}
                    if(assetPath==null)return "No offline page file is indexed for "+selected+".";
                    java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(new java.util.zip.GZIPInputStream(getAssets().open(assetPath)),"UTF-8"),8192);
                    String raw;
                    while((raw=reader.readLine())!=null){
                        org.json.JSONObject record=new org.json.JSONObject(raw);
                        if(count==0)out.append("Source: Papyrus 46 (GA P46), INTF / New Testament Virtual Manuscript Room, document 10046\n")
                            .append("Licence: Creative Commons Attribution 4.0 International (CC BY 4.0)\n")
                            .append("Original source labels and page/column/line identifiers are retained where present.\n")
                            .append("Only surviving manuscript text is included. Supplied readings are bracketed where the source encodes them; missing portions are not reconstructed.\n\n");
                        if(!record.optString("source_label").isEmpty())out.append(record.optString("source_label")).append("\n");
                        out.append("Page: ").append(record.optString("page_id")).append("\n");
                        out.append("Column: ").append(record.optJSONArray("column_ids")==null?"":record.optJSONArray("column_ids").toString()).append("\n");
                        out.append("Line: ").append(record.optJSONArray("line_ids")==null?"":record.optJSONArray("line_ids").toString()).append("\n");
                        out.append(record.optString("text")).append("\n");
                        org.json.JSONArray notes=record.optJSONArray("correction_notes");
                        if(notes!=null)for(int i=0;i<notes.length();i++)out.append("Correction note: ").append(notes.optString(i)).append("\n");
                        out.append("\n");count++;
                    }
                    reader.close();
                    return count==0?"No transcription records were found for "+selected+".":count+" source text records\n\n"+out.toString();
                }catch(Exception e){return "Unable to read the offline Papyrus 46 transcription: "+e.getMessage();}
            }
            protected void onPostExecute(String result){
                TextView view=text(result,15,ink,false);enablePassageSelection(view);
                ScrollView sv=new ScrollView(MainActivity.this);sv.setPadding(12,8,12,8);sv.addView(view);
                new android.app.AlertDialog.Builder(MainActivity.this).setTitle(selected+" · Papyrus 46")
                    .setView(sv).setNegativeButton("Back to page index",(d,w)->openPapyrus46Archive())
                    .setPositiveButton("Close",null).show();
            }
        }.executeOnExecutor(android.os.AsyncTask.THREAD_POOL_EXECUTOR);
    }

    void openPapyrus66Archive(){
        try{
            java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("papyri/p66/p66_index.json"),"UTF-8"));
            StringBuilder raw=new StringBuilder();String line;while((line=reader.readLine())!=null)raw.append(line);reader.close();
            org.json.JSONObject index=new org.json.JSONObject(raw.toString());
            org.json.JSONArray pages=index.getJSONArray("pages");
            String[] labels=new String[pages.length()];
            String[] ids=new String[pages.length()];
            for(int i=0;i<pages.length();i++){
                org.json.JSONObject page=pages.getJSONObject(i);
                ids[i]=page.optString("page_id");
                labels[i]=ids[i]+"  ·  "+page.optInt("record_count")+" text records";
            }
            new android.app.AlertDialog.Builder(this).setTitle("Papyrus 66 · Offline Page Archive")
                .setItems(labels,(dialog,which)->openPapyrus66Page(ids[which]))
                .setNegativeButton("Close",null).show();
        }catch(Exception e){
            showInfo("Papyrus 66 transcription unavailable","The offline P66 transcription was not generated in this build. "+e.getMessage());
        }
    }

    void openPapyrus66Page(String pageId){
        final String selected=pageId;
        new android.os.AsyncTask<Void,Void,String>(){
            protected String doInBackground(Void... ignored){
                StringBuilder out=new StringBuilder();int count=0;
                try{
                    java.io.BufferedReader indexReader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("papyri/p66/p66_index.json"),"UTF-8"));
                    StringBuilder indexRaw=new StringBuilder();String indexLine;while((indexLine=indexReader.readLine())!=null)indexRaw.append(indexLine);indexReader.close();
                    org.json.JSONArray pages=new org.json.JSONObject(indexRaw.toString()).getJSONArray("pages");
                    String assetPath=null;
                    for(int i=0;i<pages.length();i++){org.json.JSONObject page=pages.getJSONObject(i);if(selected.equals(page.optString("page_id"))){assetPath=page.optString("asset_file");break;}}
                    if(assetPath==null)return "No offline page file is indexed for "+selected+".";
                    java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(new java.util.zip.GZIPInputStream(getAssets().open(assetPath)),"UTF-8"),8192);
                    String raw;
                    while((raw=reader.readLine())!=null){
                        org.json.JSONObject record=new org.json.JSONObject(raw);
                        if(count==0)out.append("Source: Papyrus 66 (GA P66), INTF / New Testament Virtual Manuscript Room, document 10066\n")
                            .append("Licence: Creative Commons Attribution 4.0 International (CC BY 4.0)\n")
                            .append("Original source labels and page/column/line identifiers are retained where present.\n")
                            .append("Only surviving manuscript text is included. Supplied readings are bracketed where the source encodes them; missing portions are not reconstructed.\n\n");
                        if(!record.optString("source_label").isEmpty())out.append(record.optString("source_label")).append("\n");
                        out.append("Page: ").append(record.optString("page_id")).append("\n");
                        out.append("Column: ").append(record.optJSONArray("column_ids")==null?"":record.optJSONArray("column_ids").toString()).append("\n");
                        out.append("Line: ").append(record.optJSONArray("line_ids")==null?"":record.optJSONArray("line_ids").toString()).append("\n");
                        out.append(record.optString("text")).append("\n");
                        org.json.JSONArray notes=record.optJSONArray("correction_notes");
                        if(notes!=null)for(int i=0;i<notes.length();i++)out.append("Correction note: ").append(notes.optString(i)).append("\n");
                        out.append("\n");count++;
                    }
                    reader.close();
                    return count==0?"No transcription records were found for "+selected+".":count+" source text records\n\n"+out.toString();
                }catch(Exception e){return "Unable to read the offline Papyrus 66 transcription: "+e.getMessage();}
            }
            protected void onPostExecute(String result){
                TextView view=text(result,15,ink,false);enablePassageSelection(view);
                ScrollView sv=new ScrollView(MainActivity.this);sv.setPadding(12,8,12,8);sv.addView(view);
                new android.app.AlertDialog.Builder(MainActivity.this).setTitle(selected+" · Papyrus 66")
                    .setView(sv).setNegativeButton("Back to page index",(d,w)->openPapyrus66Archive())
                    .setPositiveButton("Close",null).show();
            }
        }.executeOnExecutor(android.os.AsyncTask.THREAD_POOL_EXECUTOR);
    }

    void openPapyrus75Archive(){
        try{
            java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("papyri/p75/p75_index.json"),"UTF-8"));
            StringBuilder raw=new StringBuilder();String line;while((line=reader.readLine())!=null)raw.append(line);reader.close();
            org.json.JSONObject index=new org.json.JSONObject(raw.toString());
            org.json.JSONArray pages=index.getJSONArray("pages");
            String[] labels=new String[pages.length()];
            String[] ids=new String[pages.length()];
            for(int i=0;i<pages.length();i++){
                org.json.JSONObject page=pages.getJSONObject(i);
                ids[i]=page.optString("page_id");
                labels[i]=ids[i]+"  ·  "+page.optInt("record_count")+" text records";
            }
            new android.app.AlertDialog.Builder(this).setTitle("Papyrus 75 · Offline Page Archive")
                .setItems(labels,(dialog,which)->openPapyrus75Page(ids[which]))
                .setNegativeButton("Close",null).show();
        }catch(Exception e){
            showInfo("Papyrus 75 transcription unavailable","The offline P75 transcription was not generated in this build. "+e.getMessage());
        }
    }

    void openPapyrus75Page(String pageId){
        final String selected=pageId;
        new android.os.AsyncTask<Void,Void,String>(){
            protected String doInBackground(Void... ignored){
                StringBuilder out=new StringBuilder();int count=0;
                try{
                    java.io.BufferedReader indexReader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("papyri/p75/p75_index.json"),"UTF-8"));
                    StringBuilder indexRaw=new StringBuilder();String indexLine;while((indexLine=indexReader.readLine())!=null)indexRaw.append(indexLine);indexReader.close();
                    org.json.JSONArray pages=new org.json.JSONObject(indexRaw.toString()).getJSONArray("pages");
                    String assetPath=null;
                    for(int i=0;i<pages.length();i++){org.json.JSONObject page=pages.getJSONObject(i);if(selected.equals(page.optString("page_id"))){assetPath=page.optString("asset_file");break;}}
                    if(assetPath==null)return "No offline page file is indexed for "+selected+".";
                    java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(new java.util.zip.GZIPInputStream(getAssets().open(assetPath)),"UTF-8"),8192);
                    String raw;
                    while((raw=reader.readLine())!=null){
                        org.json.JSONObject record=new org.json.JSONObject(raw);
                        if(count==0)out.append("Source: Papyrus 75 (GA P75), INTF / New Testament Virtual Manuscript Room, document 10075\n")
                            .append("Licence: Creative Commons Attribution 4.0 International (CC BY 4.0)\n")
                            .append("Original source labels and page/column/line identifiers are retained where present.\n")
                            .append("Only surviving manuscript text is included. Supplied readings are bracketed where the source encodes them; missing portions are not reconstructed.\n\n");
                        if(!record.optString("source_label").isEmpty())out.append(record.optString("source_label")).append("\n");
                        out.append("Page: ").append(record.optString("page_id")).append("\n");
                        out.append("Column: ").append(record.optJSONArray("column_ids")==null?"":record.optJSONArray("column_ids").toString()).append("\n");
                        out.append("Line: ").append(record.optJSONArray("line_ids")==null?"":record.optJSONArray("line_ids").toString()).append("\n");
                        out.append(record.optString("text")).append("\n");
                        org.json.JSONArray notes=record.optJSONArray("correction_notes");
                        if(notes!=null)for(int i=0;i<notes.length();i++)out.append("Correction note: ").append(notes.optString(i)).append("\n");
                        out.append("\n");count++;
                    }
                    reader.close();
                    return count==0?"No transcription records were found for "+selected+".":count+" source text records\n\n"+out.toString();
                }catch(Exception e){return "Unable to read the offline Papyrus 75 transcription: "+e.getMessage();}
            }
            protected void onPostExecute(String result){
                TextView view=text(result,15,ink,false);enablePassageSelection(view);
                ScrollView sv=new ScrollView(MainActivity.this);sv.setPadding(12,8,12,8);sv.addView(view);
                new android.app.AlertDialog.Builder(MainActivity.this).setTitle(selected+" · Papyrus 75")
                    .setView(sv).setNegativeButton("Back to page index",(d,w)->openPapyrus75Archive())
                    .setPositiveButton("Close",null).show();
            }
        }.executeOnExecutor(android.os.AsyncTask.THREAD_POOL_EXECUTOR);
    }

    void openPapyrus77Archive(){
        try{
            java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("papyri/p77/p77_index.json"),"UTF-8"));
            StringBuilder raw=new StringBuilder();String line;while((line=reader.readLine())!=null)raw.append(line);reader.close();
            org.json.JSONObject index=new org.json.JSONObject(raw.toString());
            org.json.JSONArray pages=index.getJSONArray("pages");
            String[] labels=new String[pages.length()];
            String[] ids=new String[pages.length()];
            for(int i=0;i<pages.length();i++){
                org.json.JSONObject page=pages.getJSONObject(i);
                ids[i]=page.optString("page_id");
                labels[i]=ids[i]+"  ·  "+page.optInt("record_count")+" text records";
            }
            new android.app.AlertDialog.Builder(this).setTitle("Papyrus 77 · Offline Page Archive")
                .setItems(labels,(dialog,which)->openPapyrus77Page(ids[which]))
                .setNegativeButton("Close",null).show();
        }catch(Exception e){
            showInfo("Papyrus 77 transcription unavailable","The offline P77 transcription was not generated in this build. "+e.getMessage());
        }
    }

    void openPapyrus77Page(String pageId){
        final String selected=pageId;
        new android.os.AsyncTask<Void,Void,String>(){
            protected String doInBackground(Void... ignored){
                StringBuilder out=new StringBuilder();int count=0;
                try{
                    java.io.BufferedReader indexReader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("papyri/p77/p77_index.json"),"UTF-8"));
                    StringBuilder indexRaw=new StringBuilder();String indexLine;while((indexLine=indexReader.readLine())!=null)indexRaw.append(indexLine);indexReader.close();
                    org.json.JSONArray pages=new org.json.JSONObject(indexRaw.toString()).getJSONArray("pages");
                    String assetPath=null;
                    for(int i=0;i<pages.length();i++){org.json.JSONObject page=pages.getJSONObject(i);if(selected.equals(page.optString("page_id"))){assetPath=page.optString("asset_file");break;}}
                    if(assetPath==null)return "No offline page file is indexed for "+selected+".";
                    java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(new java.util.zip.GZIPInputStream(getAssets().open(assetPath)),"UTF-8"),8192);
                    String raw;
                    while((raw=reader.readLine())!=null){
                        org.json.JSONObject record=new org.json.JSONObject(raw);
                        if(count==0)out.append("Source: Papyrus 77 (GA P77), INTF / New Testament Virtual Manuscript Room, document 10077\n")
                            .append("Licence: Creative Commons Attribution 4.0 International (CC BY 4.0)\n")
                            .append("Original source labels and page/column/line identifiers are retained where present.\n")
                            .append("Only surviving manuscript text is included. Supplied readings are bracketed where the source encodes them; missing portions are not reconstructed.\n\n");
                        if(!record.optString("source_label").isEmpty())out.append(record.optString("source_label")).append("\n");
                        out.append("Page: ").append(record.optString("page_id")).append("\n");
                        out.append("Column: ").append(record.optJSONArray("column_ids")==null?"":record.optJSONArray("column_ids").toString()).append("\n");
                        out.append("Line: ").append(record.optJSONArray("line_ids")==null?"":record.optJSONArray("line_ids").toString()).append("\n");
                        out.append(record.optString("text")).append("\n");
                        org.json.JSONArray notes=record.optJSONArray("correction_notes");
                        if(notes!=null)for(int i=0;i<notes.length();i++)out.append("Correction note: ").append(notes.optString(i)).append("\n");
                        out.append("\n");count++;
                    }
                    reader.close();
                    return count==0?"No transcription records were found for "+selected+".":count+" source text records\n\n"+out.toString();
                }catch(Exception e){return "Unable to read the offline Papyrus 77 transcription: "+e.getMessage();}
            }
            protected void onPostExecute(String result){
                TextView view=text(result,15,ink,false);enablePassageSelection(view);
                ScrollView sv=new ScrollView(MainActivity.this);sv.setPadding(12,8,12,8);sv.addView(view);
                new android.app.AlertDialog.Builder(MainActivity.this).setTitle(selected+" · Papyrus 77")
                    .setView(sv).setNegativeButton("Back to page index",(d,w)->openPapyrus77Archive())
                    .setPositiveButton("Close",null).show();
            }
        }.executeOnExecutor(android.os.AsyncTask.THREAD_POOL_EXECUTOR);
    }

    void openPapyrus72Archive(){
        try{
            java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("papyri/p72/p72_index.json"),"UTF-8"));
            StringBuilder raw=new StringBuilder();String line;while((line=reader.readLine())!=null)raw.append(line);reader.close();
            org.json.JSONObject index=new org.json.JSONObject(raw.toString());
            org.json.JSONArray pages=index.getJSONArray("pages");
            String[] labels=new String[pages.length()];
            String[] ids=new String[pages.length()];
            for(int i=0;i<pages.length();i++){
                org.json.JSONObject page=pages.getJSONObject(i);
                ids[i]=page.optString("page_id");
                labels[i]=ids[i]+"  ·  "+page.optInt("record_count")+" text records";
            }
            new android.app.AlertDialog.Builder(this).setTitle("Papyrus 72 · Offline Page Archive")
                .setItems(labels,(dialog,which)->openPapyrus72Page(ids[which]))
                .setNegativeButton("Close",null).show();
        }catch(Exception e){
            showInfo("Papyrus 72 transcription unavailable","The offline P72 transcription was not generated in this build. "+e.getMessage());
        }
    }

    void openPapyrus72Page(String pageId){
        final String selected=pageId;
        new android.os.AsyncTask<Void,Void,String>(){
            protected String doInBackground(Void... ignored){
                StringBuilder out=new StringBuilder();int count=0;
                try{
                    java.io.BufferedReader indexReader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("papyri/p72/p72_index.json"),"UTF-8"));
                    StringBuilder indexRaw=new StringBuilder();String indexLine;while((indexLine=indexReader.readLine())!=null)indexRaw.append(indexLine);indexReader.close();
                    org.json.JSONArray pages=new org.json.JSONObject(indexRaw.toString()).getJSONArray("pages");
                    String assetPath=null;
                    for(int i=0;i<pages.length();i++){org.json.JSONObject page=pages.getJSONObject(i);if(selected.equals(page.optString("page_id"))){assetPath=page.optString("asset_file");break;}}
                    if(assetPath==null)return "No offline page file is indexed for "+selected+".";
                    java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(new java.util.zip.GZIPInputStream(getAssets().open(assetPath)),"UTF-8"),8192);
                    String raw;
                    while((raw=reader.readLine())!=null){
                        org.json.JSONObject record=new org.json.JSONObject(raw);
                        if(count==0)out.append("Source: Papyrus 72 (GA P72), INTF / New Testament Virtual Manuscript Room, document 10072\n")
                            .append("Licence: Creative Commons Attribution 4.0 International (CC BY 4.0)\n")
                            .append("Original source labels and page/column/line identifiers are retained where present.\n")
                            .append("Only surviving manuscript text is included. Supplied readings are bracketed where the source encodes them; missing portions are not reconstructed.\n\n");
                        if(!record.optString("source_label").isEmpty())out.append(record.optString("source_label")).append("\n");
                        out.append("Page: ").append(record.optString("page_id")).append("\n");
                        out.append("Column: ").append(record.optJSONArray("column_ids")==null?"":record.optJSONArray("column_ids").toString()).append("\n");
                        out.append("Line: ").append(record.optJSONArray("line_ids")==null?"":record.optJSONArray("line_ids").toString()).append("\n");
                        out.append(record.optString("text")).append("\n");
                        org.json.JSONArray notes=record.optJSONArray("correction_notes");
                        if(notes!=null)for(int i=0;i<notes.length();i++)out.append("Correction note: ").append(notes.optString(i)).append("\n");
                        out.append("\n");count++;
                    }
                    reader.close();
                    return count==0?"No transcription records were found for "+selected+".":count+" source text records\n\n"+out.toString();
                }catch(Exception e){return "Unable to read the offline Papyrus 72 transcription: "+e.getMessage();}
            }
            protected void onPostExecute(String result){
                TextView view=text(result,15,ink,false);enablePassageSelection(view);
                ScrollView sv=new ScrollView(MainActivity.this);sv.setPadding(12,8,12,8);sv.addView(view);
                new android.app.AlertDialog.Builder(MainActivity.this).setTitle(selected+" · Papyrus 72")
                    .setView(sv).setNegativeButton("Back to page index",(d,w)->openPapyrus72Archive())
                    .setPositiveButton("Close",null).show();
            }
        }.executeOnExecutor(android.os.AsyncTask.THREAD_POOL_EXECUTOR);
    }

    void openPapyrus52Archive(){
        try{
            java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("papyri/p52/p52_index.json"),"UTF-8"));
            StringBuilder raw=new StringBuilder();String line;while((line=reader.readLine())!=null)raw.append(line);reader.close();
            org.json.JSONObject index=new org.json.JSONObject(raw.toString());
            org.json.JSONArray pages=index.getJSONArray("pages");
            String[] labels=new String[pages.length()];
            String[] ids=new String[pages.length()];
            for(int i=0;i<pages.length();i++){
                org.json.JSONObject page=pages.getJSONObject(i);
                ids[i]=page.optString("page_id");
                labels[i]=ids[i]+"  ·  "+page.optInt("record_count")+" text records";
            }
            new android.app.AlertDialog.Builder(this).setTitle("Papyrus 52 · Offline Page Archive")
                .setItems(labels,(dialog,which)->openPapyrus52Page(ids[which]))
                .setNegativeButton("Close",null).show();
        }catch(Exception e){
            showInfo("Papyrus 52 transcription unavailable","The offline P52 transcription was not generated in this build. "+e.getMessage());
        }
    }

    void openPapyrus52Page(String pageId){
        final String selected=pageId;
        new android.os.AsyncTask<Void,Void,String>(){
            protected String doInBackground(Void... ignored){
                StringBuilder out=new StringBuilder();int count=0;
                try{
                    java.io.BufferedReader indexReader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("papyri/p52/p52_index.json"),"UTF-8"));
                    StringBuilder indexRaw=new StringBuilder();String indexLine;while((indexLine=indexReader.readLine())!=null)indexRaw.append(indexLine);indexReader.close();
                    org.json.JSONArray pages=new org.json.JSONObject(indexRaw.toString()).getJSONArray("pages");
                    String assetPath=null;
                    for(int i=0;i<pages.length();i++){org.json.JSONObject page=pages.getJSONObject(i);if(selected.equals(page.optString("page_id"))){assetPath=page.optString("asset_file");break;}}
                    if(assetPath==null)return "No offline page file is indexed for "+selected+".";
                    java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(new java.util.zip.GZIPInputStream(getAssets().open(assetPath)),"UTF-8"),8192);
                    String raw;
                    while((raw=reader.readLine())!=null){
                        org.json.JSONObject record=new org.json.JSONObject(raw);
                        if(count==0)out.append("Source: Papyrus 52 (GA P46), INTF / New Testament Virtual Manuscript Room, document 10052\n")
                            .append("Licence: Creative Commons Attribution 4.0 International (CC BY 4.0)\n")
                            .append("Original source labels and page/column/line identifiers are retained where present.\n")
                            .append("Only surviving manuscript text is included. Supplied readings are bracketed where the source encodes them; missing portions are not reconstructed.\n\n");
                        if(!record.optString("source_label").isEmpty())out.append(record.optString("source_label")).append("\n");
                        out.append("Page: ").append(record.optString("page_id")).append("\n");
                        out.append("Column: ").append(record.optJSONArray("column_ids")==null?"":record.optJSONArray("column_ids").toString()).append("\n");
                        out.append("Line: ").append(record.optJSONArray("line_ids")==null?"":record.optJSONArray("line_ids").toString()).append("\n");
                        out.append(record.optString("text")).append("\n");
                        org.json.JSONArray notes=record.optJSONArray("correction_notes");
                        if(notes!=null)for(int i=0;i<notes.length();i++)out.append("Correction note: ").append(notes.optString(i)).append("\n");
                        out.append("\n");count++;
                    }
                    reader.close();
                    return count==0?"No transcription records were found for "+selected+".":count+" source text records\n\n"+out.toString();
                }catch(Exception e){return "Unable to read the offline Papyrus 52 transcription: "+e.getMessage();}
            }
            protected void onPostExecute(String result){
                TextView view=text(result,15,ink,false);enablePassageSelection(view);
                ScrollView sv=new ScrollView(MainActivity.this);sv.setPadding(12,8,12,8);sv.addView(view);
                new android.app.AlertDialog.Builder(MainActivity.this).setTitle(selected+" · Papyrus 52")
                    .setView(sv).setNegativeButton("Back to page index",(d,w)->openPapyrus52Archive())
                    .setPositiveButton("Close",null).show();
            }
        }.executeOnExecutor(android.os.AsyncTask.THREAD_POOL_EXECUTOR);
    }

    void openCatalogEntry(String item){
        try{
            java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("catalog/greek_manuscript_register.json"),"UTF-8"));
            StringBuilder raw=new StringBuilder();String line;while((line=reader.readLine())!=null)raw.append(line);reader.close();
            org.json.JSONArray records=new org.json.JSONObject(raw.toString()).getJSONArray("records");
            org.json.JSONObject match=null;
            String key=item.toLowerCase();
            if(key.contains("sinaiticus"))key="sinaiticus";
            else if(key.contains("vaticanus"))key="vaticanus";
            else if(key.contains("p52"))key="p52";
            else if(key.contains("p46"))key="p46";
            else if(key.contains("p66"))key="p66";
            else if(key.contains("p75"))key="p75";
            else if(key.contains("p76"))key="p76";
            else if(key.contains("p72"))key="p72";
            else if(key.contains("p77"))key="p77";
            else if(key.contains("p88"))key="p88";
            else if(key.contains("p103"))key="p103";
            else if(key.contains("p104"))key="p104";
            else if(key.contains("p45"))key="p45";
            for(int i=0;i<records.length();i++){
                org.json.JSONObject r=records.getJSONObject(i);
                if(r.optString("id").equalsIgnoreCase(key)){match=r;break;}
            }
            if(match==null){new android.app.AlertDialog.Builder(this).setTitle(item).setMessage("No verified manuscript metadata record is available yet. No transcription or manuscript reading is being claimed.").setPositiveButton("Close",null).show();return;}
            StringBuilder detail=new StringBuilder();
            detail.append("Material: ").append(match.optString("material")).append("\n");
            detail.append("Language: ").append(match.optString("language")).append("\n");
            detail.append("Date: ").append(match.optString("date_estimate")).append("\n");
            detail.append("Dating basis: ").append(match.optString("date_basis")).append("\n");
            detail.append("Surviving contents: ").append(match.optString("contents")).append("\n");
            detail.append("Condition: ").append(match.optString("condition")).append("\n");
            detail.append("Holding: ").append(match.optString("holding_institution")).append("\n");
            detail.append("Shelfmark: ").append(match.optString("shelfmark")).append("\n\n");
            detail.append("Status: ").append(match.optString("status")).append("\n\n");
            detail.append("Research caution: ").append(match.optString("caution")).append("\n\n");
            org.json.JSONObject digital=match.optJSONObject("digital_transcription_source");
            if(digital!=null){
                detail.append("Digital transcription source:\n");
                detail.append(digital.optString("title")).append("\n");
                detail.append("Version: ").append(digital.optString("version")).append("\n");
                detail.append("Format: ").append(digital.optString("format")).append("\n");
                detail.append("Licence: ").append(digital.optString("license")).append("\n");
                detail.append("Status: ").append(digital.optString("status")).append("\n");
                if(!digital.optString("bundle_status").isEmpty())detail.append("Offline bundle: ").append(digital.optString("bundle_status")).append("\n");
                if(!digital.optString("use_restriction").isEmpty())detail.append("\nUSE RESTRICTION NOTICE:\n").append(digital.optString("use_restriction")).append("\n");
                detail.append("Caution: ").append(digital.optString("caution")).append("\n");
                detail.append("Transcription source: ").append(digital.optString("source_url")).append("\n");
                detail.append("Repository: ").append(digital.optString("repository_url")).append("\n\n");
            }
            detail.append("Sources:\n");
            org.json.JSONArray urls=match.optJSONArray("source_urls");
            if(urls!=null)for(int i=0;i<urls.length();i++)detail.append(urls.optString(i)).append("\n");
            TextView view=text(detail.toString(),14,ink,false);
            view.setAutoLinkMask(android.text.util.Linkify.WEB_URLS);
            view.setMovementMethod(android.text.method.LinkMovementMethod.getInstance());
            ScrollView sv=new ScrollView(this);sv.setPadding(14,8,14,8);sv.addView(view);
            android.app.AlertDialog.Builder builder=new android.app.AlertDialog.Builder(this).setTitle(match.optString("name")).setView(sv).setPositiveButton("Close",null);
            if("Vaticanus".equalsIgnoreCase(match.optString("id")))builder.setNeutralButton("Open offline transcription",(d,w)->openVaticanusArchive());
            if("P46".equalsIgnoreCase(match.optString("id")))builder.setNeutralButton("Open offline transcription",(d,w)->openPapyrus46Archive());
            if("P52".equalsIgnoreCase(match.optString("id")))builder.setNeutralButton("Open fragment transcription",(d,w)->openPapyrus52Archive());
            if("P66".equalsIgnoreCase(match.optString("id")))builder.setNeutralButton("Open offline transcription",(d,w)->openPapyrus66Archive());
            if("P75".equalsIgnoreCase(match.optString("id")))builder.setNeutralButton("Open offline transcription",(d,w)->openPapyrus75Archive());
            if("P77".equalsIgnoreCase(match.optString("id")))builder.setNeutralButton("Open offline transcription",(d,w)->openPapyrus77Archive());
            if("P72".equalsIgnoreCase(match.optString("id")))builder.setNeutralButton("Open offline transcription",(d,w)->openPapyrus72Archive());
            builder.show();
        }catch(Exception e){
            new android.app.AlertDialog.Builder(this).setTitle("Manuscript catalogue unavailable").setMessage("The metadata register is not present in this build yet.").setPositiveButton("Close",null).show();
        }
    }

}
