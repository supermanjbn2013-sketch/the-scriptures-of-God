package org.scripturesofgod.archive;

import android.app.Activity;
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
import com.google.mlkit.nl.translate.TranslateLanguage;
import com.google.mlkit.nl.translate.Translation;
import com.google.mlkit.nl.translate.Translator;
import com.google.mlkit.nl.translate.TranslatorOptions;
import com.google.mlkit.common.model.DownloadConditions;

public class MainActivity extends Activity {
    int bg=Color.rgb(15,19,24), panel=Color.rgb(26,33,41), gold=Color.rgb(205,174,112), ink=Color.rgb(232,228,217), muted=Color.rgb(160,166,170);
    LinearLayout root, content;
    String section="Home";
    String[] translationNames={"Afrikaans","Arabic","Belarusian","Bulgarian","Bengali","Catalan","Czech","Welsh","Danish","German","Greek","English","Esperanto","Spanish","Estonian","Persian","Finnish","French","Irish","Galician","Gujarati","Hebrew","Hindi","Croatian","Haitian Creole","Hungarian","Indonesian","Icelandic","Italian","Japanese","Georgian","Kannada","Korean","Lithuanian","Latvian","Macedonian","Marathi","Malay","Maltese","Dutch","Norwegian","Polish","Portuguese","Romanian","Russian","Slovak","Slovenian","Albanian","Swedish","Swahili","Tamil","Telugu","Thai","Filipino / Tagalog","Turkish","Ukrainian","Urdu","Vietnamese","Chinese"};
    String[] translationCodes={"af","ar","be","bg","bn","ca","cs","cy","da","de","el","en","eo","es","et","fa","fi","fr","ga","gl","gu","he","hi","hr","ht","hu","id","is","it","ja","ka","kn","ko","lt","lv","mk","mr","ms","mt","nl","no","pl","pt","ro","ru","sk","sl","sq","sv","sw","ta","te","th","tl","tr","uk","ur","vi","zh"};
    String targetLanguage(){return getSharedPreferences("archive_settings",MODE_PRIVATE).getString("target_language","en");}
    String targetLanguageName(){String code=targetLanguage();for(int i=0;i<translationCodes.length;i++)if(translationCodes[i].equals(code))return translationNames[i];return "English";}
    void chooseTranslationLanguage(){
        int selected=0;for(int i=0;i<translationCodes.length;i++)if(translationCodes[i].equals(targetLanguage()))selected=i;
        new android.app.AlertDialog.Builder(this).setTitle("Automatic verse translation").setMessage("The first use of a language downloads its model (about 30 MB). After downloading, translation works offline.").setSingleChoiceItems(translationNames,selected,(dialog,which)->{
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
        entries.put("Translation Center",new ArrayList<>(Arrays.asList("English","Filipino / Tagalog","Spanish","Portuguese","French","German","Italian","Arabic","Hebrew","Greek","Aramaic","Chinese","Japanese","Korean","Indonesian","Latin")));
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
        Button languageButton=new Button(this);languageButton.setText("Automatic verse translation: "+targetLanguageName());languageButton.setTextColor(gold);languageButton.setBackground(shape(panel));LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,-2);lp.setMargins(0,8,0,12);page.addView(languageButton,lp);languageButton.setOnClickListener(v->chooseTranslationLanguage());
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
        int count=0;for(String item:data){if(q.length()==0||item.toLowerCase().contains(q.toLowerCase())){TextView row=text(item,15,ink,false);row.setBackground(shape(panel));LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,-2);p.setMargins(0,5,0,5);content.addView(row,p); row.setOnClickListener(v -> {if(section.equals("DSS Passage Concordance"))openDssConcordanceEntry(item);else if(codeFor(item)!=null)openBook(item);else if(item.toLowerCase().contains("isaiah scroll")||item.toLowerCase().contains("habakkuk")||item.toLowerCase().contains("genesis apocryphon")||item.toLowerCase().contains("community rule")||item.toLowerCase().contains("temple scroll")||item.toLowerCase().contains("war scroll"))openDssCatalogEntry(item);else openCatalogEntry(item);}); count++;}}
        if(count==0)content.addView(text("No matching entries. This archive does not fabricate missing manuscript contents or readings.",14,muted,false));
        if(section.equals("Manuscript Archive")||section.equals("Research Archive")||section.equals("Manuscript Comparison"))content.addView(text("Records are catalog placeholders until a source, transcription, date and provenance are verified and attached.",12,gold,false));
    }

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
                            if(lines==null)continue;
                            for(int k=0;k<lines.length()&&hits.size()<100;k++){
                                org.json.JSONObject entry=lines.getJSONObject(k);
                                String body=entry.optString("transcription_text");
                                String group=entry.optString("group");
                                String sourceReference=entry.optString("source_reference");
                                String passageRefs=entry.optJSONArray("passages")==null?"":entry.optJSONArray("passages").toString();
                                if(matchesExact(body,needle)||matchesExact(group,needle)||matchesExact(sourceReference,needle)||matchesExact(passageRefs,needle)){
                                    hits.add("[DSS "+record.optString("manuscript_id")+"] "+group+" line "+entry.optInt("digital_line")+"  "+body);
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
                new android.app.AlertDialog.Builder(MainActivity.this).setTitle("Exact text search: "+exact).setView(sv).setPositiveButton("Close",null).show();
            }
        }.executeOnExecutor(android.os.AsyncTask.THREAD_POOL_EXECUTOR);
    }

    void openBook(String name){
        final String bookName=name;
        final String code=codeFor(bookName);
        if(code==null)return;
        new android.os.AsyncTask<Void,Void,org.json.JSONObject>(){
            protected org.json.JSONObject doInBackground(Void... ignored){
                try{
                    java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("corpus/verses.jsonl"),"UTF-8"));
                    org.json.JSONObject result=new org.json.JSONObject();
                    org.json.JSONArray verses=new org.json.JSONArray();
                    StringBuilder metadata=new StringBuilder();String line;boolean metadataAdded=false;
                    while((line=reader.readLine())!=null){
                        org.json.JSONObject obj=new org.json.JSONObject(line);
                        String ref=obj.optString("ref");
                        if(bookName.equals(obj.optString("book"))||ref.startsWith(bookName+" ")||ref.startsWith(code+".")||ref.startsWith(code+" ")){
                            if(!metadataAdded){
                                metadata.append("Source: ").append(obj.optString("source")).append("\n");
                                metadata.append("Edition: ").append(obj.optString("edition")).append("\n");
                                metadata.append("Witness basis: ").append(obj.optString("witness_basis")).append("\n");
                                metadata.append("Text type: ").append(obj.optString("transcription_type")).append("\n");
                                metadata.append("Licence: ").append(obj.optString("license",obj.optString("text_status"))).append("\n");
                                metadata.append("Attribution: ").append(obj.optString("attribution")).append("\n");
                                metadata.append("Source URL: ").append(obj.optString("source_url")).append("\n\n");
                                metadataAdded=true;
                            }
                            String displayRef=bookName.equals(obj.optString("book"))?ref:(ref.startsWith(bookName+" ")?ref.substring(bookName.length()).trim():ref.substring(code.length()).trim());
                            org.json.JSONObject verse=new org.json.JSONObject();
                            verse.put("reference",displayRef);verse.put("text",obj.optString("text"));verse.put("language",obj.optString("language"));
                            verses.put(verse);
                        }
                    }
                    reader.close();
                    if(verses.length()==0)return null;
                    try{
                        java.io.BufferedReader coverageReader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("corpus/apocrypha_coverage.json"),"UTF-8"));
                        StringBuilder coverageRaw=new StringBuilder();String coverageLine;
                        while((coverageLine=coverageReader.readLine())!=null)coverageRaw.append(coverageLine);
                        coverageReader.close();
                        org.json.JSONObject coverage=new org.json.JSONObject(coverageRaw.toString()).optJSONObject(bookName);
                        if(coverage!=null){
                            metadata.append("Source-file coverage audit: ").append(coverage.optInt("record_count")).append(" verse records across ").append(coverage.optInt("chapter_count")).append(" source chapters.\n");
                            metadata.append(coverage.optString("scope_note")).append("\n");
                            org.json.JSONObject chapters=coverage.optJSONObject("chapters");
                            if(chapters!=null){
                                metadata.append("Chapter coverage:\n");
                                java.util.Iterator<String> keys=chapters.keys();
                                while(keys.hasNext()){
                                    String chapter=keys.next();org.json.JSONObject detail=chapters.optJSONObject(chapter);
                                    if(detail!=null)metadata.append("Chapter ").append(chapter).append(": ").append(detail.optInt("verse_count")).append(" source verses (").append(detail.optInt("first_source_verse")).append("–").append(detail.optInt("last_source_verse")).append(")\n");
                                }
                            }
                            metadata.append("\n");
                        }
                    }catch(Exception coverageError){}
                    result.put("metadata",metadata.toString());result.put("verses",verses);return result;
                }catch(Exception e){return null;}
            }
            protected void onPostExecute(org.json.JSONObject result){
                if(result==null){
                    new android.app.AlertDialog.Builder(MainActivity.this).setMessage("No bundled text record was found for "+bookName+".").setPositiveButton("OK",null).show();return;
                }
                LinearLayout list=new LinearLayout(MainActivity.this);list.setOrientation(1);list.setPadding(12,8,12,8);
                TextView meta=text(result.optString("metadata"),12,muted,false);meta.setAutoLinkMask(android.text.util.Linkify.WEB_URLS);meta.setMovementMethod(android.text.method.LinkMovementMethod.getInstance());list.addView(meta);
                org.json.JSONArray verses=result.optJSONArray("verses");
                if(verses!=null)for(int i=0;i<verses.length();i++){
                    org.json.JSONObject verse=verses.optJSONObject(i);if(verse==null)continue;
                    String reference=verse.optString("reference"),body=verse.optString("text"),language=verse.optString("language");
                    TextView row=text(reference+"\n"+body+"\n\nTap to translate",15,ink,false);
                    row.setBackground(shape(panel));LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,-2);p.setMargins(0,4,0,4);list.addView(row,p);
                    row.setOnClickListener(v->translateVerse(reference,body,language));
                }
                ScrollView sv=new ScrollView(MainActivity.this);sv.setPadding(8,8,8,8);sv.addView(list);
                new android.app.AlertDialog.Builder(MainActivity.this).setTitle(bookName+" — tap any verse to translate").setView(sv).setPositiveButton("Close",null).show();
            }
        }.executeOnExecutor(android.os.AsyncTask.THREAD_POOL_EXECUTOR);
    }

    void translateVerse(String reference,String sourceText,String sourceLanguage){
        String source;
        if("he".equals(sourceLanguage))source="he";
        else if("grc".equals(sourceLanguage))source="el";
        else if("la".equals(sourceLanguage)){new android.app.AlertDialog.Builder(this).setTitle("Translation unavailable").setMessage("The on-device translation model does not support Latin source text yet.").setPositiveButton("Close",null).show();return;}
        else {new android.app.AlertDialog.Builder(this).setTitle("Translation unavailable").setMessage("No supported source-language mapping is registered for this text.").setPositiveButton("Close",null).show();return;}
        String target=targetLanguage();
        if(source.equals(target)){new android.app.AlertDialog.Builder(this).setTitle(reference).setMessage("This verse is already in your selected language.\n\n"+sourceText).setPositiveButton("Close",null).show();return;}
        String supportedSource=TranslateLanguage.fromLanguageTag(source);
        String supportedTarget=TranslateLanguage.fromLanguageTag(target);
        if(supportedSource==null||supportedTarget==null){new android.app.AlertDialog.Builder(this).setTitle("Language unavailable").setMessage("The selected language is not supported by the on-device translation engine.").setPositiveButton("Close",null).show();return;}
        TranslatorOptions options=new TranslatorOptions.Builder().setSourceLanguage(supportedSource).setTargetLanguage(supportedTarget).build();
        Translator translator=Translation.getClient(options);
        android.app.ProgressDialog progress=new android.app.ProgressDialog(this);progress.setMessage("Preparing "+targetLanguageName()+" translation…");progress.setCancelable(false);progress.show();
        translator.downloadModelIfNeeded(new DownloadConditions.Builder().build())
            .addOnSuccessListener(unused->translator.translate(sourceText)
                .addOnSuccessListener(translated->{
                    if(progress.isShowing())progress.dismiss();
                    new android.app.AlertDialog.Builder(MainActivity.this).setTitle(reference+" — "+targetLanguageName())
                        .setMessage("SOURCE TEXT\n"+sourceText+"\n\n"+targetLanguageName().toUpperCase()+" TRANSLATION\n"+translated+"\n\nMachine translation for study assistance only. The model is designed for modern-language translation, so its output from ancient Hebrew or Koine Greek may be inaccurate. It is not a manuscript reading, a critical translation, or a substitute for checking the source text.")
                        .setPositiveButton("Close",null).show();translator.close();
                })
                .addOnFailureListener(error->{if(progress.isShowing())progress.dismiss();translator.close();new android.app.AlertDialog.Builder(MainActivity.this).setTitle("Translation failed").setMessage("The verse could not be translated. Check your connection and try again.").setPositiveButton("Close",null).show();}))
            .addOnFailureListener(error->{if(progress.isShowing())progress.dismiss();translator.close();new android.app.AlertDialog.Builder(MainActivity.this).setTitle("Translation model unavailable").setMessage("Connect to the internet once to download the language model, then retry.").setPositiveButton("Close",null).show();});
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
                    detail.append("\n  Hebrew transcription: ").append(lineEntry.optString("transcription_text", "not imported"));
                    detail.append("\n  Source: ").append(lineEntry.optString("source_reference", "not recorded"));
                    if(lineEntry.has("note"))detail.append("\n  Note: ").append(lineEntry.optString("note"));
                    detail.append("\n");
                }
                detail.append("Mapping policy: ").append(match.optString("line_map_policy")).append("\n");
            }
            org.json.JSONArray additionalSources=match.optJSONArray("additional_transcription_sources");
            if(additionalSources!=null)for(int sourceIndex=0;sourceIndex<additionalSources.length();sourceIndex++){
                org.json.JSONObject source=additionalSources.getJSONObject(sourceIndex);
                detail.append("\\nAdditional transcription source (kept separate):\\n");
                detail.append(source.optString("title")).append("\\n");
                detail.append("Provider: ").append(source.optString("provider")).append("\\n");
                detail.append("Version: ").append(source.optString("version")).append("\\n");
                detail.append("Format: ").append(source.optString("format")).append("\\n");
                detail.append("Licence: ").append(source.optString("license")).append("\\n");
                detail.append("Attribution: ").append(source.optString("attribution")).append("\\n");
                detail.append("Source URL: ").append(source.optString("url")).append("\\n");
                detail.append("Use: ").append(source.optString("use")).append("\\n");
                detail.append("Caution: ").append(source.optString("caution")).append("\\n");
                org.json.JSONArray sourceSections=source.optJSONArray("sections");
                if(sourceSections!=null)for(int sectionIndex=0;sectionIndex<sourceSections.length();sectionIndex++){
                    org.json.JSONObject section=sourceSections.getJSONObject(sectionIndex);
                    detail.append("\\nFragment group: ").append(section.optString("fragment_group")).append("\\n");
                    detail.append("PDF heading: ").append(section.optString("pdf_heading")).append("\\n");
                    detail.append("Passage references: ");
                    org.json.JSONArray refs=section.optJSONArray("passage_refs");
                    if(refs!=null)for(int refIndex=0;refIndex<refs.length();refIndex++){if(refIndex>0)detail.append("; ");detail.append(refs.optString(refIndex));}
                    detail.append("\\nTranscription text (PDF text layer):\\n").append(section.optString("pdf_text_lines")).append("\\n");
                    detail.append("Section caution: ").append(section.optString("caution")).append("\\n");
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
            TextView view=text(detail.toString(),14,ink,false);view.setAutoLinkMask(android.text.util.Linkify.WEB_URLS);view.setMovementMethod(android.text.method.LinkMovementMethod.getInstance());
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
