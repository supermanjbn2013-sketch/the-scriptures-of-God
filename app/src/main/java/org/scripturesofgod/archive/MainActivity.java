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
    String returnSection="Home";
    String[] translationNames={"Afrikaans","Arabic","Belarusian","Bulgarian","Bengali","Catalan","Czech","Welsh","Danish","German","Greek","English","Esperanto","Spanish","Estonian","Persian","Finnish","French","Irish","Galician","Gujarati","Hebrew","Hindi","Croatian","Haitian Creole","Hungarian","Indonesian","Icelandic","Italian","Japanese","Georgian","Kannada","Korean","Lithuanian","Latvian","Macedonian","Marathi","Malay","Maltese","Dutch","Norwegian","Polish","Portuguese","Romanian","Russian","Slovak","Slovenian","Albanian","Swedish","Swahili","Tamil","Telugu","Thai","Filipino / Tagalog","Turkish","Ukrainian","Urdu","Vietnamese","Chinese"};
    String[] translationCodes={"af","ar","be","bg","bn","ca","cs","cy","da","de","el","en","eo","es","et","fa","fi","fr","ga","gl","gu","he","hi","hr","ht","hu","id","is","it","ja","ka","kn","ko","lt","lv","mk","mr","ms","mt","nl","no","pl","pt","ro","ru","sk","sl","sq","sv","sw","ta","te","th","tl","tr","uk","ur","vi","zh"};
    String targetLanguage(){return getSharedPreferences("archive_settings",MODE_PRIVATE).getString("target_language","en");}
    String targetLanguageName(){String code=targetLanguage();for(int i=0;i<translationCodes.length;i++)if(translationCodes[i].equals(code))return translationNames[i];return "English";}
    void chooseTranslationLanguage(){
        int selected=0;for(int i=0;i<translationCodes.length;i++)if(translationCodes[i].equals(targetLanguage()))selected=i;
        new android.app.AlertDialog.Builder(this).setTitle("Preferred translation language").setMessage("Choose the target language for external translation tools. Google Translate and other phone translators may still produce inaccurate results for ancient Hebrew and Koine Greek.").setSingleChoiceItems(translationNames,selected,(dialog,which)->{
            getSharedPreferences("archive_settings",MODE_PRIVATE).edit().putString("target_language",translationCodes[which]).apply();
            dialog.dismiss();show();
        }).setNegativeButton("Cancel",null).show();
    }
    Map<String,ArrayList<String>> entries=new LinkedHashMap<>();
    String[] sections={"Home","Hebrew Scriptures","Prophets","Apostolic Writings","Apocrypha and Deuterocanonical Writings","Ancient Referenced Books","Other Ancient Writings","Manuscript Archive","DSS Passage Concordance","Translation Center","Manuscript Comparison","Research Archive","Favorites","Reading History"};
    @Override public void onCreate(Bundle b){super.onCreate(b); seed(); show();}
    void seed(){
        entries.put("Hebrew Scriptures",new ArrayList<>(Arrays.asList("Genesis","Exodus","Leviticus","Numbers","Deuteronomy","Joshua","Judges","Ruth","1 Samuel","2 Samuel","1 Kings","2 Kings","1 Chronicles","2 Chronicles","Ezra","Nehemiah","Esther","Job","Psalms","Proverbs","Ecclesiastes","Song of Songs","Isaiah","Jeremiah","Lamentations","Ezekiel","Daniel","Hosea","Joel","Amos","Obadiah","Jonah","Micah","Nahum","Habakkuk","Zephaniah","Haggai","Zechariah","Malachi")));
        entries.put("Prophets",new ArrayList<>(Arrays.asList("Isaiah","Jeremiah","Ezekiel","Daniel","Hosea","Joel","Amos","Obadiah","Jonah","Micah","Nahum","Habakkuk","Zephaniah","Haggai","Zechariah","Malachi")));
        entries.put("Apostolic Writings",new ArrayList<>(Arrays.asList("Matthew","Mark","Luke","John","Acts","Romans","1 Corinthians","2 Corinthians","Galatians","Ephesians","Philippians","Colossians","1 Thessalonians","2 Thessalonians","1 Timothy","2 Timothy","Titus","Philemon","Hebrews","James","1 Peter","2 Peter","1 John","2 John","3 John","Jude","Revelation")));
        entries.put("Apocrypha and Deuterocanonical Writings",new ArrayList<>(Arrays.asList("1 Esdras","Tobit","Judith","Esther (Greek)","Wisdom of Solomon","Sirach","Baruch","Letter of Jeremiah","1 Maccabees","2 Maccabees","3 Maccabees","4 Maccabees","Susanna (Old Greek)","Susanna (Theodotion)","Daniel (Old Greek)","Daniel (Theodotion)","Bel and the Dragon (Old Greek)","Bel and the Dragon (Theodotion)","Odes","Prayer of Manasseh (Greek)","Psalm 151","2 Esdras / 4 Ezra (Latin)","Prayer of Manasseh (Latin)")));
        entries.put("Other Ancient Writings",new ArrayList<>(Arrays.asList("1 Enoch","Jubilees","Didache","Shepherd of Hermas","Gospel of Thomas")));
        entries.put("Manuscript Archive",new ArrayList<>(Arrays.asList("Dead Sea Scrolls (DSS)","Great Isaiah Scroll (1QIsaᵃ)","Pesher Habakkuk (1QpHab)","Genesis Apocryphon (1QapGen)","Community Rule (1QS)","Temple Scroll (11Q19)","War Scroll (1QM)","Masoretic Text","Septuagint","Samaritan Pentateuch","Papyrus 46 (P46)","Papyrus 52 (P52)","Papyrus 66 (P66)","Papyrus 75 (P75)","Codex Vaticanus","Codex Sinaiticus","Codex Alexandrinus")));
        entries.put("DSS Passage Concordance",new ArrayList<>(Arrays.asList("4Q26 Lev d — Leviticus","4Q27 Num b — Numbers","4Q31 Deut d — Deuteronomy","4Q47 Josh a — Joshua","4Q53 Sam c — Samuel")));
        entries.put("Translation Center",new ArrayList<>(Arrays.asList("AI translation is integrated into every Scripture passage","Preferred translation language","AI connection settings")));
        entries.put("Manuscript Comparison",new ArrayList<>(Arrays.asList("Compare witness transcriptions","Review additions and omissions","Inspect textual variants","Trace quotations and parallels")));
        entries.put("Research Archive",new ArrayList<>(Arrays.asList("Source metadata","Authorship assessments","Composition dates","Language and provenance","Fragment and witness records","Research notes")));
        entries.put("Favorites",new ArrayList<>()); entries.put("Reading History",new ArrayList<>());
    }
    GradientDrawable shape(int color){GradientDrawable d=new GradientDrawable();d.setColor(color);d.setCornerRadius(18);return d;}
    TextView text(String s,int size,int color,boolean bold){TextView t=new TextView(this);t.setText(s);t.setTextSize(size);t.setTextColor(color);if(bold)t.setTypeface(Typeface.DEFAULT,Typeface.BOLD);t.setPadding(16,12,16,12);return t;}
    void show(){
        root=new LinearLayout(this);root.setOrientation(1);root.setBackgroundColor(bg);
        ScrollView scroll=new ScrollView(this); LinearLayout page=new LinearLayout(this);page.setOrientation(1);page.setPadding(16,18,16,24);scroll.addView(page);
        TextView brand=text("THE SCRIPTURES OF GOD",20,gold,true);page.addView(brand);
        page.addView(text("Ancient Manuscript Archive  ·  Scripture Research",12,muted,false));
        EditText search=new EditText(this);search.setSingleLine(true);search.setTextColor(ink);search.setHintTextColor(muted);search.setHint("Search exact word or phrase, reference, manuscript…");search.setPadding(16,10,16,10);search.setBackground(shape(panel));LinearLayout.LayoutParams sp=new LinearLayout.LayoutParams(-1,-2);sp.setMargins(0,18,0,14);page.addView(search,sp);
        Button corpusSearch=new Button(this);corpusSearch.setText("Search complete text corpus");corpusSearch.setTextColor(ink);corpusSearch.setBackground(shape(panel));page.addView(corpusSearch,new LinearLayout.LayoutParams(-1,-2));
        corpusSearch.setOnClickListener(v->{String query=search.getText().toString().trim();if(query.length()>0)searchCorpus(query);});
        Button languageButton=new Button(this);languageButton.setText("Translation status: verified sources only");languageButton.setTextColor(gold);languageButton.setBackground(shape(panel));LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,-2);lp.setMargins(0,8,0,12);page.addView(languageButton,lp);languageButton.setOnClickListener(v->chooseTranslationLanguage());
        content=new LinearLayout(this);content.setOrientation(1);page.addView(content);
        search.addTextChangedListener(new TextWatcher(){public void beforeTextChanged(CharSequence s,int st,int c,int a){} public void onTextChanged(CharSequence s,int st,int before,int count){render(s.toString());}public void afterTextChanged(Editable e){}});
        render("");root.addView(scroll,new LinearLayout.LayoutParams(-1,0,1));
        HorizontalScrollView navScroll=new HorizontalScrollView(this);LinearLayout nav=new LinearLayout(this);nav.setPadding(8,8,8,8);nav.setBackgroundColor(panel);
        for(String s:sections){TextView b=text(s,12,s.equals(section)?gold:ink,true);b.setOnClickListener(v->{section=s;show();});nav.addView(b);}navScroll.addView(nav);root.addView(navScroll,new LinearLayout.LayoutParams(-1,-2));
        setContentView(root);
    }
    void render(String q){
        content.removeAllViews();
        content.addView(text(section,22,ink,true));
        if(section.equals("Home")){
            content.addView(text("A research archive for ancient witnesses, original languages, textual variants and translation comparison.",15,muted,false));
            for(String s:sections){if(!s.equals("Home")){TextView tile=text("›  "+s,16,ink,true);tile.setBackground(shape(panel));LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,-2);p.setMargins(0,7,0,7);content.addView(tile,p);tile.setOnClickListener(v->{section=s;show();});}}
            return;
        }
        ArrayList<String> data=entries.get(section); if(data==null)data=new ArrayList<>();
        int count=0;for(String item:data){if(q.length()==0||item.toLowerCase().contains(q.toLowerCase())){TextView row=text(item,15,ink,false);row.setBackground(shape(panel));LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,-2);p.setMargins(0,5,0,5);content.addView(row,p); row.setOnClickListener(v -> {returnSection=section;if(section.equals("Translation Center")){if(item.equals("Preferred translation language"))chooseTranslationLanguage();else showAiConnectionSettings();}else if(section.equals("DSS Passage Concordance"))openDssConcordanceEntry(item);else if(codeFor(item)!=null)openBook(item);else if(item.toLowerCase().contains("isaiah scroll")||item.toLowerCase().contains("habakkuk")||item.toLowerCase().contains("genesis apocryphon")||item.toLowerCase().contains("community rule")||item.toLowerCase().contains("temple scroll")||item.toLowerCase().contains("war scroll"))openDssCatalogEntry(item);else openCatalogEntry(item);}); count++;}}
        if(count==0)content.addView(text("No matching entries. This archive does not fabricate missing manuscript contents or readings.",14,muted,false));
        if(section.equals("Manuscript Archive")||section.equals("Research Archive")||section.equals("Manuscript Comparison"))content.addView(text("Records are catalog placeholders until a source, transcription, date and provenance are verified and attached.",12,gold,false));
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
                TextView view=text(result.toString(),14,ink,false);view.setTextIsSelectable(true);
                ScrollView sv=new ScrollView(MainActivity.this);sv.setPadding(14,8,14,8);sv.addView(view);
                new android.app.AlertDialog.Builder(MainActivity.this).setTitle("Exact text search: "+exact).setView(sv).setNegativeButton("Back to "+returnSection,(d,w)->{}).setNeutralButton("Home",(d,w)->{section="Home";show();}).setPositiveButton("Close",null).show();
            }
        }.executeOnExecutor(android.os.AsyncTask.THREAD_POOL_EXECUTOR);
    }

    void openBook(String name){
        final String bookName=name;
        final String code=codeFor(bookName);
        if(code==null){new android.app.AlertDialog.Builder(this).setMessage("No text mapping is registered for "+bookName+".").setPositiveButton("Close",null).show();return;}
        new android.os.AsyncTask<Void,Void,org.json.JSONObject>(){
            protected org.json.JSONObject doInBackground(Void... ignored){
                org.json.JSONObject result=new org.json.JSONObject();
                org.json.JSONArray verses=new org.json.JSONArray();
                StringBuilder metadata=new StringBuilder();
                int scanned=0;
                try{
                    java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("corpus/verses.jsonl"),"UTF-8"),65536);
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
                LinearLayout list=new LinearLayout(MainActivity.this);list.setOrientation(1);list.setPadding(12,8,12,8);
                list.addView(text(count+" verses loaded from the offline corpus",13,gold,true));
                TextView meta=text(result.optString("metadata"),12,muted,false);
                meta.setAutoLinkMask(android.text.util.Linkify.WEB_URLS);
                meta.setMovementMethod(android.text.method.LinkMovementMethod.getInstance());
                list.addView(meta);
                String currentChapter="";
                for(int i=0;i<count;i++){
                    org.json.JSONObject verse=verses.optJSONObject(i);if(verse==null)continue;
                    String reference=verse.optString("reference"),body=verse.optString("text"),language=verse.optString("language");
                    String chapter=reference.contains(":")?reference.substring(0,reference.indexOf(':')):"";
                    if(!chapter.equals(currentChapter)&&chapter.length()>0){
                        currentChapter=chapter;
                        list.addView(text("Chapter "+chapter,18,gold,true));
                    }
                    TextView row=text(reference+"\n"+body+"\n\nTap to translate",16,ink,false);
                    row.setBackground(shape(panel));
                    LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,-2);
                    p.setMargins(0,4,0,4);list.addView(row,p);
                    row.setOnClickListener(v->translateVerse(reference,body,language));
                }
                ScrollView sv=new ScrollView(MainActivity.this);sv.setFillViewport(true);sv.setPadding(8,8,8,8);sv.addView(list);
                new android.app.AlertDialog.Builder(MainActivity.this).setTitle(bookName+" — "+count+" verses").setView(sv).setNegativeButton("Back to "+returnSection,(d,w)->{}).setNeutralButton("Home",(d,w)->{section="Home";show();}).setPositiveButton("Close",null).show();
            }
        }.executeOnExecutor(android.os.AsyncTask.THREAD_POOL_EXECUTOR);
    }

    private static final String AI_MODEL="gemini-3.1-flash-lite";
    private static final String[] AI_MODES={"Modern English translation","Older English style (Early Modern)","Literal translation","Word-for-word analysis","Grammar and meaning explanation"};
    private String getAiKey(){
        try{
            String packed=getSharedPreferences("archive_ai",MODE_PRIVATE).getString("api_key_encrypted","");
            if(packed.isEmpty()){packed=getSharedPreferences("AiTranslatorActivity",MODE_PRIVATE).getString("api_key_encrypted","");if(!packed.isEmpty())getSharedPreferences("archive_ai",MODE_PRIVATE).edit().putString("api_key_encrypted",packed).apply();}
            if(packed.isEmpty())return "";
            byte[] all=android.util.Base64.decode(packed,android.util.Base64.NO_WRAP);
            byte[] iv=java.util.Arrays.copyOfRange(all,0,12), encrypted=java.util.Arrays.copyOfRange(all,12,all.length);
            javax.crypto.Cipher cipher=javax.crypto.Cipher.getInstance("AES/GCM/NoPadding");
            cipher.init(javax.crypto.Cipher.DECRYPT_MODE,getAiSecretKey(),new javax.crypto.spec.GCMParameterSpec(128,iv));
            return new String(cipher.doFinal(encrypted),"UTF-8");
        }catch(Exception e){return "";}
    }
    private javax.crypto.SecretKey getAiSecretKey()throws Exception{
        java.security.KeyStore store=java.security.KeyStore.getInstance("AndroidKeyStore");store.load(null);
        String alias="scriptures_of_god_ai_key";
        if(store.containsAlias(alias))return (javax.crypto.SecretKey)store.getKey(alias,null);
        javax.crypto.KeyGenerator generator=javax.crypto.KeyGenerator.getInstance(android.security.keystore.KeyProperties.KEY_ALGORITHM_AES,"AndroidKeyStore");
        generator.init(new android.security.keystore.KeyGenParameterSpec.Builder(alias,android.security.keystore.KeyProperties.PURPOSE_ENCRYPT|android.security.keystore.KeyProperties.PURPOSE_DECRYPT)
            .setBlockModes(android.security.keystore.KeyProperties.BLOCK_MODE_GCM).setEncryptionPaddings(android.security.keystore.KeyProperties.ENCRYPTION_PADDING_NONE).setRandomizedEncryptionRequired(true).build());
        return generator.generateKey();
    }
    private void saveAiKey(String value)throws Exception{
        if(value.isEmpty()){getSharedPreferences("archive_ai",MODE_PRIVATE).edit().remove("api_key_encrypted").apply();return;}
        javax.crypto.Cipher cipher=javax.crypto.Cipher.getInstance("AES/GCM/NoPadding");
        cipher.init(javax.crypto.Cipher.ENCRYPT_MODE,getAiSecretKey());
        byte[] encrypted=cipher.doFinal(value.getBytes("UTF-8")),iv=cipher.getIV(),packed=new byte[iv.length+encrypted.length];
        System.arraycopy(iv,0,packed,0,iv.length);System.arraycopy(encrypted,0,packed,iv.length,encrypted.length);
        getSharedPreferences("archive_ai",MODE_PRIVATE).edit().putString("api_key_encrypted",android.util.Base64.encodeToString(packed,android.util.Base64.NO_WRAP)).apply();
    }
    void showAiConnectionSettings(){
        LinearLayout box=new LinearLayout(this);box.setOrientation(1);box.setPadding(18,8,18,4);
        EditText key=new EditText(this);key.setSingleLine(true);key.setHint("Paste your Gemini API key");key.setInputType(129);key.setText(getAiKey());box.addView(key);
        box.addView(text("Your key is encrypted on this device. AI translation sends submitted text to Google Gemini. Free-tier limits and Google's data-use terms apply.",12,muted,false));
        new android.app.AlertDialog.Builder(this).setTitle("AI connection settings").setView(box)
            .setNeutralButton("Get free key",(d,w)->startActivity(new Intent(Intent.ACTION_VIEW,android.net.Uri.parse("https://aistudio.google.com/app/apikey"))))
            .setNegativeButton("Cancel",null)
            .setPositiveButton("Save key",(d,w)->{try{saveAiKey(key.getText().toString().trim());Toast.makeText(this,"AI key saved securely",Toast.LENGTH_SHORT).show();}catch(Exception e){Toast.makeText(this,"Could not save key: "+e.getMessage(),Toast.LENGTH_LONG).show();}}).show();
    }
    void translateVerse(String reference,String sourceText,String sourceLanguage){
        LinearLayout box=new LinearLayout(this);box.setOrientation(1);box.setPadding(18,8,18,8);
        String languageName="he".equals(sourceLanguage)?"Ancient Hebrew":("grc".equals(sourceLanguage)?"Koine Greek":("la".equals(sourceLanguage)?"Latin":("en".equals(sourceLanguage)?"English":"source language")));
        box.addView(text(reference+"  ·  "+languageName,13,gold,true));
        TextView original=text(sourceText,16,ink,false);original.setTextIsSelectable(true);box.addView(original);
        Spinner mode=new Spinner(this);
        ArrayAdapter<String> adapter=new ArrayAdapter<>(this,android.R.layout.simple_spinner_item,AI_MODES);
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);mode.setAdapter(adapter);box.addView(mode);
        TextView result=text("Translating automatically with AI…",14,ink,false);result.setBackground(shape(panel));box.addView(result);
        Button settings=new Button(this);settings.setText("AI connection settings");settings.setOnClickListener(v->showAiConnectionSettings());box.addView(settings);
        Button external=new Button(this);external.setText("Open Google Translate");external.setOnClickListener(v->openGoogleTranslate(sourceText,targetLanguage()));box.addView(external);
        android.app.AlertDialog dialog=new android.app.AlertDialog.Builder(this).setTitle(reference+" — AI Translation").setView(box).setNegativeButton("Close",null).create();
        dialog.show();
        mode.setOnItemSelectedListener(new android.widget.AdapterView.OnItemSelectedListener(){
            boolean first=true;
            public void onNothingSelected(android.widget.AdapterView<?> parent){}
            public void onItemSelected(android.widget.AdapterView<?> parent,View view,int position,long id){
                if(first){first=false;return;}
                requestAiTranslation(reference,sourceText,sourceLanguage,AI_MODES[position],result);
            }
        });
        requestAiTranslation(reference,sourceText,sourceLanguage,AI_MODES[0],result);
    }
    private void requestAiTranslation(String reference,String sourceText,String sourceLanguage,String selectedMode,TextView output){
        String key=getAiKey().trim();
        if(key.isEmpty()){
            output.setText("Add your free Gemini API key in AI connection settings, then tap this passage again.");
            return;
        }
        output.setText("AI is translating…");
        String lang="he".equals(sourceLanguage)?"Ancient Hebrew":("grc".equals(sourceLanguage)?"Koine Greek":("la".equals(sourceLanguage)?"Latin":"automatically detected"));
        String target=targetLanguageName();
        String prompt="You are a cautious scholarly translation assistant. Translate the supplied passage into "+target+". Mode: "+selectedMode+". Source language: "+lang+". Preserve the supplied text; never invent missing words, clauses, manuscript readings, witnesses or citations. Distinguish translation from interpretation and reconstruction. Mark uncertain readings and explain ambiguity. Do not claim manuscript attestation without evidence supplied. For Hebrew or Koine Greek, explain morphology and syntax only when supportable. For Older English style, use restrained Early Modern English, not Anglo-Saxon Old English. For word-for-word analysis, give source form, transliteration, lemma if identifiable, morphology, lexical range and contextual sense. Separate observed linguistic facts from interpretation. Include a clear result and concise language notes. Reference: "+reference+"\nTEXT:\n"+sourceText;
        new Thread(()->{
            String answer=null,error=null;java.net.HttpURLConnection connection=null;
            try{
                java.net.URL url=new java.net.URL("https://generativelanguage.googleapis.com/v1beta/models/"+AI_MODEL+":generateContent");
                connection=(java.net.HttpURLConnection)url.openConnection();connection.setRequestMethod("POST");connection.setConnectTimeout(20000);connection.setReadTimeout(90000);connection.setDoOutput(true);
                connection.setRequestProperty("Content-Type","application/json");connection.setRequestProperty("x-goog-api-key",key);
                org.json.JSONObject part=new org.json.JSONObject().put("text",prompt);
                org.json.JSONObject payload=new org.json.JSONObject().put("contents",new org.json.JSONArray().put(new org.json.JSONObject().put("parts",new org.json.JSONArray().put(part)))).put("generationConfig",new org.json.JSONObject().put("maxOutputTokens",4096));
                try(java.io.OutputStream out=connection.getOutputStream()){out.write(payload.toString().getBytes("UTF-8"));}
                int status=connection.getResponseCode();java.io.InputStream stream=status>=200&&status<300?connection.getInputStream():connection.getErrorStream();
                StringBuilder raw=new StringBuilder();try(java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(stream,"UTF-8"))){String line;while((line=reader.readLine())!=null)raw.append(line);}
                org.json.JSONObject response=new org.json.JSONObject(raw.toString());
                if(status<200||status>=300){org.json.JSONObject e=response.optJSONObject("error");error=e==null?"AI service returned HTTP "+status:e.optString("message","AI request failed");}
                else{org.json.JSONArray candidates=response.optJSONArray("candidates");if(candidates==null||candidates.length()==0)error="AI returned no translation.";else{org.json.JSONArray parts=candidates.getJSONObject(0).optJSONObject("content").optJSONArray("parts");StringBuilder text=new StringBuilder();if(parts!=null)for(int i=0;i<parts.length();i++)text.append(parts.getJSONObject(i).optString("text",""));answer=text.toString().trim();if(answer.isEmpty())error="AI returned an empty response.";}}
            }catch(Exception e){error=e.getMessage()==null?e.getClass().getSimpleName():e.getMessage();}
            finally{if(connection!=null)connection.disconnect();}
            final String a=answer,e=error;
            runOnUiThread(()->output.setText(a!=null?a:"Translation unavailable: "+e));
        }).start();
    }

    void openGoogleTranslate(String sourceText,String targetLanguageCode){
        try{
            String target=targetLanguageCode==null||targetLanguageCode.trim().isEmpty()?"en":targetLanguageCode;
            String url="https://translate.google.com/?sl=auto&tl="+android.net.Uri.encode(target)+"&text="+android.net.Uri.encode(sourceText)+"&op=translate";
            Intent intent=new Intent(Intent.ACTION_VIEW,android.net.Uri.parse(url));
            startActivity(intent);
        }catch(Exception e){
            new android.app.AlertDialog.Builder(this).setMessage("Google Translate could not be opened.").setPositiveButton("Close",null).show();
        }
    }

    void shareVerseForTranslation(String reference,String sourceText){
        try{
            Intent intent=new Intent(Intent.ACTION_SEND);
            intent.setType("text/plain");
            intent.putExtra(Intent.EXTRA_SUBJECT,reference);
            intent.putExtra(Intent.EXTRA_TEXT,reference+"\n"+sourceText);
            startActivity(Intent.createChooser(intent,"Open with a translator"));
        }catch(Exception e){
            new android.app.AlertDialog.Builder(this).setMessage("No compatible sharing or translation app is available.").setPositiveButton("Close",null).show();
        }
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
            new android.app.AlertDialog.Builder(this).setTitle(match.optString("name")).setView(sv).setPositiveButton("Close",null).show();
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
                    @Override public void onClick(View widget){translateVerse(selectedReference,selectedText,"he");}
                    @Override public void updateDrawState(android.text.TextPaint paint){paint.setColor(gold);paint.setUnderlineText(true);}
                },range[0],range[1],android.text.Spanned.SPAN_EXCLUSIVE_EXCLUSIVE);
            }
            view.setText(clickableText);view.setAutoLinkMask(android.text.util.Linkify.WEB_URLS);view.setMovementMethod(android.text.method.LinkMovementMethod.getInstance());
            ScrollView sv=new ScrollView(this);sv.setPadding(14,8,14,8);sv.addView(view);
            new android.app.AlertDialog.Builder(this).setTitle(match.optString("manuscript_id")).setView(sv).setPositiveButton("Close",null).show();
        }catch(Exception e){new android.app.AlertDialog.Builder(this).setTitle("Concordance unavailable").setMessage("The DSS passage concordance is not present in this build.").setPositiveButton("Close",null).show();}
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
            new android.app.AlertDialog.Builder(this).setTitle(match.optString("name")).setView(sv).setPositiveButton("Close",null).show();
        }catch(Exception e){
            new android.app.AlertDialog.Builder(this).setTitle("Manuscript catalogue unavailable").setMessage("The metadata register is not present in this build yet.").setPositiveButton("Close",null).show();
        }
    }

}
