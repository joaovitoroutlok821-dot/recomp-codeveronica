package org.libsdl.app;

import android.app.Activity;
import android.os.Bundle;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.view.Gravity;
import android.widget.*;

public final class GameSettingsActivity extends Activity {
  private SharedPreferences p;
  private LinearLayout body;
  private int red = Color.rgb(210, 15, 28);
  public void onCreate(Bundle b) {
    super.onCreate(b);
    p = getSharedPreferences("recvx_settings", MODE_PRIVATE);
    LinearLayout root = new LinearLayout(this);
    root.setOrientation(LinearLayout.VERTICAL);
    root.setPadding(18,18,18,18);
    root.setBackgroundColor(Color.rgb(5,8,14));
    TextView title = new TextView(this);
    title.setText("RESIDENT EVIL — CONFIGURAÇÕES");
    title.setTextColor(Color.WHITE); title.setTextSize(22);
    title.setGravity(Gravity.CENTER); root.addView(title);
    body = new LinearLayout(this); body.setOrientation(LinearLayout.VERTICAL);
    ScrollView scroll = new ScrollView(this); scroll.addView(body);
    root.addView(scroll, new LinearLayout.LayoutParams(-1,0,1));
    String[] names = {"Gráficos","Desempenho","Controles","Áudio"};
    LinearLayout nav = new LinearLayout(this);
    for (String n : names) {
      Button x = new Button(this); x.setText(n); x.setTextSize(11);
      nav.addView(x,new LinearLayout.LayoutParams(0,-2,1));
      x.setOnClickListener(v -> show(n));
    }
    root.addView(nav);
    LinearLayout actions = new LinearLayout(this);
    Button reset = new Button(this); reset.setText("Restaurar padrões");
    reset.setOnClickListener(v -> { p.edit().clear().apply(); show("Gráficos"); });
    Button apply = new Button(this); apply.setText("Aplicar");
    apply.setOnClickListener(v -> finish());
    actions.addView(reset,new LinearLayout.LayoutParams(0,-2,1));
    actions.addView(apply,new LinearLayout.LayoutParams(0,-2,1));
    root.addView(actions);
    setContentView(root);
    show("Gráficos");
  }
  private void heading(String s) {
    TextView t = new TextView(this); t.setText(s); t.setTextColor(red);
    t.setTextSize(19); t.setPadding(8,16,8,8); body.addView(t);
  }
  private void disabled(String s) {
    TextView t = new TextView(this); t.setText(s); t.setTextColor(0xffaab2bd);
    t.setPadding(8,10,8,10); body.addView(t);
  }
  private void show(String tab) {
    body.removeAllViews();
    if (tab.equals("Gráficos")) {
      heading("Gráficos");
      Spinner res = new Spinner(this);
      String[] modes = {"720p (1280 x 720)","1080p (1920 x 1080)"};
      res.setAdapter(new ArrayAdapter<String>(this,android.R.layout.simple_spinner_dropdown_item,modes));
      res.setSelection(p.getInt("resolution",1));
      res.setOnItemSelectedListener(new android.widget.AdapterView.OnItemSelectedListener() {
        public void onNothingSelected(android.widget.AdapterView<?> a) {}
        public void onItemSelected(android.widget.AdapterView<?> a, android.view.View v,int pos,long id) { p.edit().putInt("resolution",pos).apply(); }
      });
      body.addView(res);
      disabled("Escala de renderização — indisponível no renderer atual.");
      disabled("Qualidade de imagem — presets ainda não integrados.");
      disabled("Filtro: Bilinear (único filtro habilitado neste APK).");
      disabled("FSR/CAS, nitidez e anti-aliasing — desativados nesta compilação.");
      disabled("Partículas e proporção manual — aguardam suporte do runtime.");
    } else if (tab.equals("Desempenho")) {
      heading("Desempenho");
      disabled("Limite de FPS — ainda não existe limitador configurável.");
      disabled("V-Sync — opção Android ainda não validada.");
      Switch fps = new Switch(this); fps.setText("Contador de FPS");
      fps.setTextColor(Color.WHITE); fps.setChecked(p.getBoolean("show_fps",true));
      fps.setOnCheckedChangeListener((v,on) -> p.edit().putBoolean("show_fps",on).apply());
      body.addView(fps);
      disabled("Cache de shaders e redução de efeitos — não expostos pelo runtime.");
    } else if (tab.equals("Controles")) {
      heading("Controles");
      Spinner mode = new Spinner(this);
      String[] choices = {"Automático","Sempre mostrar","Sempre ocultar"};
      mode.setAdapter(new ArrayAdapter<String>(this,android.R.layout.simple_spinner_dropdown_item,choices));
      mode.setSelection(p.getInt("touch_mode",0));
      mode.setOnItemSelectedListener(new android.widget.AdapterView.OnItemSelectedListener() {
        public void onNothingSelected(android.widget.AdapterView<?> a) {}
        public void onItemSelected(android.widget.AdapterView<?> a, android.view.View v,int pos,long id) { p.edit().putInt("touch_mode",pos).apply(); }
      });
      body.addView(mode);
      disabled("Automático: ocultar controles táteis somente após entrada física confirmada.");
      disabled("Mover botões, tamanho e opacidade — editor ainda em implementação.");
      disabled("Bluetooth — diagnóstico pendente de validação no aparelho.");
    } else {
      heading("Áudio");
      disabled("Volume geral, música e efeitos — aguardam integração com o mixer do jogo.");
    }
  }
}