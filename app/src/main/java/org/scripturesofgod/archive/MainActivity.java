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

public class MainActivity extends Activity {
    int bg=Color.rgb(15,19,24), panel=Color.rgb(26,33,41), gold=Color.rgb(205,174,112), ink=Color.rgb(232,228,217), muted=Color.rgb(160,166,170);
    LinearLayout root, content;
    String section="Home";
    Map<String,ArrayList<String>> entries=new LinkedHashMap<>();
    String[] sections={"Home","Hebrew Scriptures","Prophets","Apostolic Writings","Ancient Referenced Books","Other Ancient Writings","Manuscript Archive","Translation Center","Manuscript Comparison","Research Archive","Favorites","Reading History"};
    @Override public void onCreate(Bundle b){super.onCreate(b); seed(); show();}
    void seed(){
        entries.put("Hebrew Scriptures",new ArrayList<>(Arrays.asList("Genesis","Exodus","Leviticus","Numbers","Deuteronomy","Joshua","Judges","Ruth","1 Samuel","2 Samuel","1 Kings","2 Kings","1 Chronicles","2 Chronicles","Ezra","Nehemiah","Esther","Job","Psalms","Proverbs","Ecclesiastes","Song of Songs","Isaiah","Jeremiah","Lamentations","Ezekiel","Daniel","Hosea","Joel","Amos","Obadiah","Jonah","Micah","Nahum","Habakkuk","Zephaniah","Haggai","Zechariah","Malachi")));
        entries.put("Prophets",new ArrayList<>(Arrays.asList("Isaiah","Jeremiah","Ezekiel","Daniel","Hosea","Joel","Amos","Obadiah","Jonah","Micah","Nahum","Habakkuk","Zephaniah","Haggai","Zechariah","Malachi")));
        entries.put("Apostolic Writings",new ArrayList<>(Arrays.asList("Matthew","Mark","Luke","John","Acts","Romans","1 Corinthians","2 Corinthians","Galatians","Ephesians","Philippians","Colossians","1 Thessalonians","2 Thessalonians","1 Timothy","2 Timothy","Titus","Philemon","Hebrews","James","1 Peter","2 Peter","1 John","2 John","3 John","Jude","Revelation")));
        entries.put("Ancient Referenced Books",new ArrayList<>(Arrays.asList("Book of Jasher — referenced in Joshua 10:13 and 2 Samuel 1:18","Book of the Wars of the LORD — Numbers 21:14","Records of Samuel, Nathan and Gad — 1 Chronicles 29:29","Acts of Solomon — 1 Kings 11:41","Book of the Sayings of Iddo — 2 Chronicles 13:22","Earlier letter to Corinth — referenced in 1 Corinthians 5:9")));
        entries.put("Other Ancient Writings",new ArrayList<>(Arrays.asList("1 Enoch","Jubilees","Didache","Shepherd of Hermas","Gospel of Thomas")));
        entries.put("Manuscript Archive",new ArrayList<>(Arrays.asList("Dead Sea Scrolls (DSS)","Great Isaiah Scroll (1QIsaᵃ)","Pesher Habakkuk (1QpHab)","Genesis Apocryphon (1QapGen)","Community Rule (1QS)","Masoretic Text","Septuagint","Samaritan Pentateuch","Papyrus 46 (P46)","Papyrus 52 (P52)","Papyrus 66 (P66)","Papyrus 75 (P75)","Codex Vaticanus","Codex Sinaiticus","Codex Alexandrinus")));
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
        int count=0;for(String item:data){if(q.length()==0||item.toLowerCase().contains(q.toLowerCase())){TextView row=text(item,15,ink,false);row.setBackground(shape(panel));LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,-2);p.setMargins(0,5,0,5);content.addView(row,p); row.setOnClickListener(v -> {if(codeFor(item)!=null)openBook(item);else if(item.toLowerCase().contains("isaiah scroll")||item.toLowerCase().contains("habakkuk")||item.toLowerCase().contains("genesis apocryphon")||item.toLowerCase().contains("community rule"))openDssCatalogEntry(item);else openCatalogEntry(item);}); count++;}}
        if(count==0)content.addView(text("No matching entries. This archive does not fabricate missing manuscript contents or readings.",14,muted,false));
        if(section.equals("Manuscript Archive")||section.equals("Research Archive")||section.equals("Manuscript Comparison"))content.addView(text("Records are catalog placeholders until a source, transcription, date and provenance are verified and attached.",12,gold,false));
    }

    String codeFor(String name){
        String[][] pairs={{"Genesis","Gen"},{"Exodus","Exod"},{"Leviticus","Lev"},{"Numbers","Num"},{"Deuteronomy","Deut"},{"Joshua","Josh"},{"Judges","Judg"},{"Ruth","Ruth"},{"1 Samuel","1Sam"},{"2 Samuel","2Sam"},{"1 Kings","1Kgs"},{"2 Kings","2Kgs"},{"1 Chronicles","1Chr"},{"2 Chronicles","2Chr"},{"Ezra","Ezra"},{"Nehemiah","Neh"},{"Esther","Esth"},{"Job","Job"},{"Psalms","Ps"},{"Proverbs","Prov"},{"Ecclesiastes","Eccl"},{"Song of Songs","Song"},{"Isaiah","Isa"},{"Jeremiah","Jer"},{"Lamentations","Lam"},{"Ezekiel","Ezek"},{"Daniel","Dan"},{"Hosea","Hos"},{"Joel","Joel"},{"Amos","Amos"},{"Obadiah","Obad"},{"Jonah","Jonah"},{"Micah","Mic"},{"Nahum","Nah"},{"Habakkuk","Hab"},{"Zephaniah","Zeph"},{"Haggai","Hag"},{"Zechariah","Zech"},{"Malachi","Mal"},{"Matthew","Matt"},{"Mark","Mark"},{"Luke","Luke"},{"John","John"},{"Acts","Acts"},{"Romans","Rom"},{"1 Corinthians","1Cor"},{"2 Corinthians","2Cor"},{"Galatians","Gal"},{"Ephesians","Eph"},{"Philippians","Phil"},{"Colossians","Col"},{"1 Thessalonians","1Thess"},{"2 Thessalonians","2Thess"},{"1 Timothy","1Tim"},{"2 Timothy","2Tim"},{"Titus","Titus"},{"Philemon","Phlm"},{"Hebrews","Heb"},{"James","Jas"},{"1 Peter","1Pet"},{"2 Peter","2Pet"},{"1 John","1John"},{"2 John","2John"},{"3 John","3John"},{"Jude","Jude"},{"Revelation","Rev"}};
        for(String[] p:pairs) if(p[0].equals(name)) return p[1]; return null;
    }
    void openBook(String name){
        String code=codeFor(name); if(code==null)return;
        try{
            java.io.BufferedReader reader=new java.io.BufferedReader(new java.io.InputStreamReader(getAssets().open("corpus/verses.jsonl"),"UTF-8"));
            StringBuilder body=new StringBuilder(); String line; int found=0;
            while((line=reader.readLine())!=null){
                org.json.JSONObject obj=new org.json.JSONObject(line); String ref=obj.optString("ref");
                if(ref.startsWith(code+"." ) || ref.startsWith(code+" ")){
                    body.append(ref.substring(code.length()).trim()).append("  ").append(obj.optString("text")).append("\n\n"); found++;
                }
            } reader.close();
            if(found==0){new android.app.AlertDialog.Builder(this).setMessage("No bundled text record was found for "+name+".").setPositiveButton("OK",null).show();return;}
            TextView view=text(body.toString(),16,ink,false); view.setTextIsSelectable(true);
            ScrollView sv=new ScrollView(this);sv.setPadding(16,12,16,12);sv.addView(view);
            new android.app.AlertDialog.Builder(this).setTitle(name+" — source text").setView(sv).setPositiveButton("Close",null).show();
        }catch(Exception e){new android.app.AlertDialog.Builder(this).setTitle("Text data not available").setMessage("The offline corpus is not present in this build.").setPositiveButton("OK",null).show();}
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
