package org.scripturesofgod.archive;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.view.View;
import android.widget.*;
import org.json.JSONArray;
import org.json.JSONObject;
import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;
import java.security.KeyStore;
import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.GCMParameterSpec;
import android.security.keystore.KeyGenParameterSpec;
import android.security.keystore.KeyProperties;
import android.util.Base64;

public class AiTranslatorActivity extends Activity {
    private final int bg=Color.rgb(15,19,24), panel=Color.rgb(26,33,41), gold=Color.rgb(205,174,112), ink=Color.rgb(232,228,217), muted=Color.rgb(160,166,170);
    private EditText source;
    private TextView result;
    private Spinner mode, language, target;
    private Button translate;
    private static final String MODEL="gemini-3.1-flash-lite";
    private final String[] targetNames={"Afrikaans","Arabic","Belarusian","Bulgarian","Bengali","Catalan","Czech","Welsh","Danish","German","Greek","English","Esperanto","Spanish","Estonian","Persian","Finnish","French","Irish","Galician","Gujarati","Hebrew","Hindi","Croatian","Haitian Creole","Hungarian","Indonesian","Icelandic","Italian","Japanese","Georgian","Kannada","Korean","Lithuanian","Latvian","Macedonian","Marathi","Malay","Maltese","Dutch","Norwegian","Polish","Portuguese","Romanian","Russian","Slovak","Slovenian","Albanian","Swedish","Swahili","Tamil","Telugu","Thai","Filipino / Tagalog","Turkish","Ukrainian","Urdu","Vietnamese","Chinese"};
    private final String[] targetCodes={"af","ar","be","bg","bn","ca","cs","cy","da","de","el","en","eo","es","et","fa","fi","fr","ga","gl","gu","he","hi","hr","ht","hu","id","is","it","ja","ka","kn","ko","lt","lv","mk","mr","ms","mt","nl","no","pl","pt","ro","ru","sk","sl","sq","sv","sw","ta","te","th","tl","tr","uk","ur","vi","zh"};

    @Override public void onCreate(Bundle state){
        super.onCreate(state);
        build();
        if(getIntent()!=null){
            String passage=getIntent().getStringExtra("passage_text");
            String sourceCode=getIntent().getStringExtra("source_language");
            if(passage!=null&&!passage.isEmpty())source.setText(passage);
            String ref=getIntent().getStringExtra("passage_reference");
            if(ref!=null&&!ref.isEmpty())setTitle(ref+" — AI Translation");
            if(sourceCode!=null&&language!=null){
                int index="he".equals(sourceCode)?1:("grc".equals(sourceCode)?2:("arc".equals(sourceCode)?3:("la".equals(sourceCode)?4:("en".equals(sourceCode)?5:0))));
                language.setSelection(index);
            }
            if(getIntent().getBooleanExtra("open_connection_settings",false))showKeyDialog();
        }
    }
    private GradientDrawable shape(int color){GradientDrawable d=new GradientDrawable();d.setColor(color);d.setCornerRadius(16);return d;}
    private TextView label(String value,int size,int color,boolean bold){TextView t=new TextView(this);t.setText(value);t.setTextSize(size);t.setTextColor(color);if(bold)t.setTypeface(Typeface.DEFAULT,Typeface.BOLD);t.setPadding(4,9,4,7);return t;}
    private Spinner spinner(String[] values){
        Spinner s=new Spinner(this);ArrayAdapter<String> a=new ArrayAdapter<>(this,android.R.layout.simple_spinner_item,values);a.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);s.setAdapter(a);return s;
    }
    private void build(){
        LinearLayout page=new LinearLayout(this);page.setOrientation(1);page.setPadding(16,14,16,18);page.setBackgroundColor(bg);
        ScrollView scroll=new ScrollView(this);LinearLayout body=new LinearLayout(this);body.setOrientation(1);scroll.addView(body);
        body.addView(label("AI TRANSLATION WORKSPACE",21,gold,true));
        body.addView(label("Original-language study and English style conversion",13,muted,false));
        Button key=new Button(this);key.setText("AI connection settings");key.setTextColor(ink);key.setBackground(shape(panel));body.addView(key);key.setOnClickListener(v->showKeyDialog());
        body.addView(label(getSavedKey().trim().isEmpty()?"API key: Not saved — enter it once in AI connection settings.":"API key: Saved securely on this device. It will be reused automatically.",12,muted,false));
        body.addView(label("Translation / study mode",14,ink,true));
        mode=spinner(new String[]{"Modern English translation","Older English style (Early Modern)","Literal translation","Word-for-word analysis","Grammar and meaning explanation"});body.addView(mode);
        body.addView(label("Input language",14,ink,true));
        language=spinner(new String[]{"Detect automatically","Ancient Hebrew","Koine Greek","Aramaic","Latin","Modern English"});body.addView(language);
        body.addView(label("Output language",14,ink,true));
        target=spinner(targetNames);body.addView(target);
        String savedCode=getSharedPreferences("archive_settings",MODE_PRIVATE).getString("target_language","en");
        String preferredName=getIntent()==null?null:getIntent().getStringExtra("preferred_target_language");
        int selectedTarget=11;for(int i=0;i<targetNames.length;i++)if((preferredName!=null&&preferredName.equals(targetNames[i]))||((preferredName==null||preferredName.isEmpty())&&targetCodes[i].equals(savedCode)))selectedTarget=i;
        target.setSelection(selectedTarget);
        target.setOnItemSelectedListener(new android.widget.AdapterView.OnItemSelectedListener(){
            public void onItemSelected(android.widget.AdapterView<?> p,View v,int position,long id){getSharedPreferences("archive_settings",MODE_PRIVATE).edit().putString("target_language",targetCodes[position]).apply();getSharedPreferences("ai_connection",MODE_PRIVATE).edit().putString("target_language",targetNames[position]).apply();}
            public void onNothingSelected(android.widget.AdapterView<?> p){}
        });
        body.addView(label("Original text or English passage",14,ink,true));
        source=new EditText(this);source.setTextColor(ink);source.setHintTextColor(muted);source.setHint("Paste or type the text to translate…");source.setGravity(48);source.setMinLines(5);source.setPadding(14,12,14,12);source.setBackground(shape(panel));body.addView(source,new LinearLayout.LayoutParams(-1,-2));
        translate=new Button(this);translate.setText("Translate / Analyze");translate.setTextColor(Color.BLACK);translate.setBackground(shape(gold));LinearLayout.LayoutParams bp=new LinearLayout.LayoutParams(-1,-2);bp.topMargin=14;body.addView(translate,bp);translate.setOnClickListener(v->runTranslation());
        body.addView(label("AI result",16,gold,true));
        result=label("Your translation and analysis will appear here.",14,ink,false);result.setTextIsSelectable(true);result.setBackground(shape(panel));body.addView(result,new LinearLayout.LayoutParams(-1,-2));
        body.addView(label("Research safeguards",14,gold,true));
        body.addView(label("AI output is a research aid, not a manuscript witness or verified critical edition. It must distinguish the surviving text from reconstruction, identify uncertainty, and never invent missing words. Compare its claims with the manuscript record and published scholarly editions.",12,muted,false));
        Button back=new Button(this);back.setText("Return to archive");back.setOnClickListener(v->finish());body.addView(back);
        page.addView(scroll,new LinearLayout.LayoutParams(-1,0,1));setContentView(page);
    }
    private void showKeyDialog(){
        LinearLayout box=new LinearLayout(this);box.setOrientation(1);box.setPadding(18,8,18,4);
        EditText key=new EditText(this);key.setSingleLine(true);key.setHint("Paste your Gemini API key");key.setInputType(129);key.setText(getSavedKey());box.addView(key);
        TextView note=label("The app does not include a shared key. Each user connects their own free-tier key. Requests send the text you submit to Google Gemini. Google's free tier may use submitted content to improve its products. Do not submit private material.",12,muted,false);box.addView(note);
        new AlertDialog.Builder(this).setTitle("Connect AI translation").setView(box)
            .setNeutralButton("Get free API key",(d,w)->{startActivity(new Intent(Intent.ACTION_VIEW,Uri.parse("https://aistudio.google.com/app/apikey")));})
            .setNegativeButton("Cancel",null)
            .setPositiveButton("Save key",(d,w)->{try{saveApiKey(key.getText().toString().trim());Toast.makeText(this,"AI connection saved securely on this device",Toast.LENGTH_SHORT).show();}catch(Exception ex){Toast.makeText(this,"Could not secure the API key: "+ex.getMessage(),Toast.LENGTH_LONG).show();}}).show();
    }
    private String makePrompt(String text){
        String selectedMode=mode.getSelectedItem().toString();
        String inputLanguage=language.getSelectedItem().toString();
        String outputLanguage=target.getSelectedItem().toString();
        StringBuilder p=new StringBuilder();
        p.append("You are a cautious scholarly translation assistant inside an ancient manuscript research archive.\n");
        p.append("Task mode: ").append(selectedMode).append(".\nInput language: ").append(inputLanguage).append(".\nOutput language: ").append(outputLanguage).append(".\n");
        p.append("Rules: preserve the supplied text; do not invent words, clauses, manuscript readings, citations, or source witnesses. Distinguish translation from interpretation and reconstruction. Mark uncertain readings and explain why. Do not claim that a reading occurs in a manuscript unless the user supplied that manuscript evidence. For Hebrew or Koine Greek, explain significant morphology and syntax only when supportable; identify lexical alternatives rather than hiding ambiguity. Do not silently harmonize variants.\n");
        if(selectedMode.equals("Modern English translation"))p.append("Give a clear, faithful modern translation first, then brief notes on important ambiguities and grammar.");
        else if(selectedMode.startsWith("Older English"))p.append("Render the supplied English into restrained Early Modern English style (roughly 16th–17th century wording), not Anglo-Saxon Old English. Preserve the exact meaning and do not add theology or archaic claims. If the input is not English, translate it into this style only after giving a clear modern-English base rendering.");
        else if(selectedMode.equals("Literal translation"))p.append("Give a close, minimally interpretive rendering. Preserve meaningful word order where possible, then explain where the source language requires different English syntax.");
        else if(selectedMode.equals("Word-for-word analysis"))p.append("Create a word-by-word table with source form, transliteration, lemma when reasonably identifiable, morphology, basic lexical range, and contextual sense. Then provide a literal rendering. Mark uncertain parsing.");
        else p.append("Explain grammar, syntax, morphology, semantic range, and competing interpretations. Separate observed linguistic facts from interpretive conclusions.");
        p.append("\nUse headings: RESULT, LITERAL SENSE, LANGUAGE NOTES, UNCERTAINTIES. Omit sections that do not apply.\n\nTEXT:\n").append(text);
        return p.toString();
    }

    private android.content.SharedPreferences keyPreferences(){
        android.content.SharedPreferences current=getSharedPreferences("ai_connection",MODE_PRIVATE);
        if(current.getString("api_key_encrypted","").isEmpty()){
            String previous=getPreferences(0).getString("api_key_encrypted","");
            if(!previous.isEmpty()){
                current.edit().putString("api_key_encrypted",previous).commit();
                getPreferences(0).edit().remove("api_key_encrypted").commit();
            }
        }
        return current;
    }
    private String getSavedKey(){
        try{
            String packed=keyPreferences().getString("api_key_encrypted","");
            if(packed.isEmpty())return "";
            byte[] all=Base64.decode(packed,Base64.NO_WRAP);
            byte[] iv=java.util.Arrays.copyOfRange(all,0,12);
            byte[] encrypted=java.util.Arrays.copyOfRange(all,12,all.length);
            Cipher cipher=Cipher.getInstance("AES/GCM/NoPadding");
            cipher.init(Cipher.DECRYPT_MODE,getSecretKey(),new GCMParameterSpec(128,iv));
            return new String(cipher.doFinal(encrypted),"UTF-8");
        }catch(Exception e){return "";}
    }
    private void saveApiKey(String value)throws Exception{
        if(value.isEmpty()){keyPreferences().edit().remove("api_key_encrypted").commit();return;}
        Cipher cipher=Cipher.getInstance("AES/GCM/NoPadding");
        cipher.init(Cipher.ENCRYPT_MODE,getSecretKey());
        byte[] encrypted=cipher.doFinal(value.getBytes("UTF-8"));
        byte[] iv=cipher.getIV();byte[] packed=new byte[iv.length+encrypted.length];
        System.arraycopy(iv,0,packed,0,iv.length);System.arraycopy(encrypted,0,packed,iv.length,encrypted.length);
        boolean saved=keyPreferences().edit().putString("api_key_encrypted",Base64.encodeToString(packed,Base64.NO_WRAP)).commit();
        if(!saved||!value.equals(getSavedKey()))throw new Exception("Saved key could not be verified. Please try again.");
    }
    private SecretKey getSecretKey()throws Exception{
        KeyStore store=KeyStore.getInstance("AndroidKeyStore");store.load(null);
        String alias="scriptures_of_god_ai_key";
        if(store.containsAlias(alias))return (SecretKey)store.getKey(alias,null);
        KeyGenerator generator=KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES,"AndroidKeyStore");
        generator.init(new KeyGenParameterSpec.Builder(alias,KeyProperties.PURPOSE_ENCRYPT|KeyProperties.PURPOSE_DECRYPT)
            .setBlockModes(KeyProperties.BLOCK_MODE_GCM).setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE).setRandomizedEncryptionRequired(true).build());
        return generator.generateKey();
    }

    private void runTranslation(){
        String text=source.getText().toString().trim();
        if(text.isEmpty()){source.setError("Enter text first");return;}
        String key=getSavedKey().trim();
        if(key.isEmpty()){showKeyDialog();return;}
        translate.setEnabled(false);translate.setText("Working…");result.setText("The AI is analyzing the supplied text…");
        final String prompt=makePrompt(text), apiKey=key;
        new Thread(()->{
            String answer=null,error=null;HttpURLConnection connection=null;
            try{
                URL url=new URL("https://generativelanguage.googleapis.com/v1beta/models/"+MODEL+":generateContent");
                connection=(HttpURLConnection)url.openConnection();connection.setRequestMethod("POST");connection.setConnectTimeout(20000);connection.setReadTimeout(90000);connection.setDoOutput(true);
                connection.setRequestProperty("Content-Type","application/json");connection.setRequestProperty("x-goog-api-key",apiKey);
                JSONObject part=new JSONObject().put("text",prompt);
                JSONObject body=new JSONObject().put("contents",new JSONArray().put(new JSONObject().put("parts",new JSONArray().put(part))))
                    .put("generationConfig",new JSONObject().put("maxOutputTokens",4096));
                try(OutputStream out=connection.getOutputStream()){out.write(body.toString().getBytes("UTF-8"));}
                int status=connection.getResponseCode();InputStream stream=status>=200&&status<300?connection.getInputStream():connection.getErrorStream();
                StringBuilder raw=new StringBuilder();try(BufferedReader reader=new BufferedReader(new InputStreamReader(stream,"UTF-8"))){String line;while((line=reader.readLine())!=null)raw.append(line);}
                JSONObject response=new JSONObject(raw.toString());
                if(status<200||status>=300){JSONObject e=response.optJSONObject("error");error=e==null?("AI service returned HTTP "+status):e.optString("message","AI service returned HTTP "+status);}
                else{
                    JSONArray candidates=response.optJSONArray("candidates");
                    if(candidates==null||candidates.length()==0)error="The AI returned no translation. Try again with a shorter passage.";
                    else{
                        JSONObject candidate=candidates.getJSONObject(0);JSONObject content=candidate.optJSONObject("content");JSONArray parts=content==null?null:content.optJSONArray("parts");StringBuilder out=new StringBuilder();
                        if(parts!=null)for(int i=0;i<parts.length();i++)out.append(parts.getJSONObject(i).optString("text",""));
                        answer=out.toString().trim();if(answer.isEmpty())error="The AI returned an empty response.";
                    }
                }
            }catch(Exception ex){error=ex.getMessage()==null?ex.getClass().getSimpleName():ex.getMessage();}
            finally{if(connection!=null)connection.disconnect();}
            final String a=answer,e=error;
            runOnUiThread(()->{translate.setEnabled(true);translate.setText("Translate / Analyze");result.setText(a!=null?a:"Translation unavailable: "+e);});
        }).start();
    }
}
