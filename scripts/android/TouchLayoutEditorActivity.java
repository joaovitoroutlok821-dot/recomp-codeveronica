package org.libsdl.app;

import android.app.Activity;
import android.os.Bundle;
import android.content.Context;
import android.content.SharedPreferences;
import android.content.pm.ActivityInfo;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.RectF;
import android.view.MotionEvent;
import android.view.View;
import android.widget.Toast;

public final class TouchLayoutEditorActivity extends Activity {
  @Override public void onCreate(Bundle state) {
    super.onCreate(state);
    setRequestedOrientation(ActivityInfo.SCREEN_ORIENTATION_LANDSCAPE);
    getWindow().setStatusBarColor(Color.rgb(4, 7, 12));
    getWindow().setNavigationBarColor(Color.BLACK);
    setContentView(new EditorView(this));
  }

  private static final class EditorView extends View {
    private static final String[] LABELS = {"A", "B", "X", "Y", "BACK", "START", "LB", "RB"};
    private static final float[] DEFAULT_X = {0.84f, 0.92f, 0.76f, 0.84f, 0.43f, 0.57f, 0.12f, 0.88f};
    private static final float[] DEFAULT_Y = {0.78f, 0.70f, 0.70f, 0.62f, 0.90f, 0.90f, 0.18f, 0.18f};
    private final SharedPreferences prefs;
    private final Paint paint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final float[] xs = new float[9];
    private final float[] ys = new float[9];
    private int selected = -1;

    EditorView(Context context) {
      super(context);
      prefs = context.getSharedPreferences("recvx_settings", MODE_PRIVATE);
      load();
      setLayerType(View.LAYER_TYPE_SOFTWARE, null);
    }

    private void load() {
      xs[0] = prefs.getFloat("touch_stick_x", 0.17f);
      ys[0] = prefs.getFloat("touch_stick_y", 0.76f);
      for (int i = 0; i < 8; i++) {
        xs[i + 1] = prefs.getFloat("touch_btn_x_" + i, DEFAULT_X[i]);
        ys[i + 1] = prefs.getFloat("touch_btn_y_" + i, DEFAULT_Y[i]);
      }
    }

    private float radius(int index) {
      float base = Math.min(getWidth(), getHeight());
      if (index == 0) return base * 0.135f;
      int b = index - 1;
      return base * ((b == 4 || b == 5) ? 0.043f :
                     (b == 6 || b == 7) ? 0.052f : 0.058f);
    }

    private void persist() {
      SharedPreferences.Editor e = prefs.edit();
      e.putFloat("touch_stick_x", xs[0]).putFloat("touch_stick_y", ys[0]);
      for (int i = 0; i < 8; i++) {
        e.putFloat("touch_btn_x_" + i, xs[i + 1]);
        e.putFloat("touch_btn_y_" + i, ys[i + 1]);
      }
      e.apply();
    }

    private void reset() {
      xs[0] = 0.17f; ys[0] = 0.76f;
      for (int i = 0; i < 8; i++) { xs[i + 1] = DEFAULT_X[i]; ys[i + 1] = DEFAULT_Y[i]; }
      persist();
      invalidate();
      Toast.makeText(getContext(), "Posições padrão restauradas", Toast.LENGTH_SHORT).show();
    }

    @Override protected void onDraw(Canvas c) {
      super.onDraw(c);
      float w = getWidth(), h = getHeight(), base = Math.min(w, h);
      c.drawColor(Color.rgb(5, 8, 14));
      paint.setColor(Color.WHITE); paint.setTextSize(base * 0.035f); paint.setFakeBoldText(true);
      c.drawText("PERSONALIZAR CONTROLES", base * 0.04f, base * 0.065f, paint);
      paint.setFakeBoldText(false); paint.setTextSize(base * 0.022f);
      paint.setColor(Color.LTGRAY);
      c.drawText("Arraste cada botão ou o joystick para a posição desejada. Toque em CONCLUIR para voltar.", base * 0.04f, base * 0.105f, paint);

      RectF reset = new RectF(w - base * 0.22f, base * 0.025f, w - base * 0.04f, base * 0.09f);
      paint.setColor(Color.rgb(105, 0, 12)); c.drawRoundRect(reset, base * 0.018f, base * 0.018f, paint);
      paint.setColor(Color.WHITE); paint.setTextSize(base * 0.022f); paint.setTextAlign(Paint.Align.CENTER);
      c.drawText("PADRÃO", reset.centerX(), reset.centerY() + base * 0.008f, paint);
      RectF done = new RectF(w - base * 0.22f, h - base * 0.095f, w - base * 0.04f, h - base * 0.025f);
      paint.setColor(Color.rgb(190, 0, 18)); c.drawRoundRect(done, base * 0.018f, base * 0.018f, paint);
      paint.setColor(Color.WHITE); c.drawText("CONCLUIR", done.centerX(), done.centerY() + base * 0.008f, paint);
      paint.setTextAlign(Paint.Align.LEFT);

      for (int i = 0; i < 9; i++) {
        float x = xs[i] * w, y = ys[i] * h, r = radius(i);
        paint.setStyle(Paint.Style.FILL);
        paint.setColor(i == selected + 1 ? Color.argb(125, 255, 35, 45) : Color.argb(82, 220, 225, 235));
        c.drawCircle(x, y, r, paint);
        paint.setStyle(Paint.Style.STROKE); paint.setStrokeWidth(base * 0.006f);
        paint.setColor(Color.WHITE); c.drawCircle(x, y, r, paint);
        paint.setStyle(Paint.Style.FILL); paint.setTextAlign(Paint.Align.CENTER);
        paint.setTextSize(i == 0 ? base * 0.055f : r * ((i == 5 || i == 6 || i == 7 || i == 8) ? 0.48f : 0.9f));
        String label = i == 0 ? "✥" : LABELS[i - 1];
        c.drawText(label, x, y + paint.getTextSize() * 0.34f, paint);
      }
      paint.setTextAlign(Paint.Align.LEFT);
    }

    @Override public boolean onTouchEvent(MotionEvent e) {
      float x = e.getX(), y = e.getY(), w = getWidth(), h = getHeight(), base = Math.min(w, h);
      if (e.getActionMasked() == MotionEvent.ACTION_DOWN) {
        if (x > w - base * 0.23f && y < base * 0.11f) { reset(); return true; }
        if (x > w - base * 0.23f && y > h - base * 0.11f) { persist(); finishActivity(); return true; }
        selected = -2;
        float best = Float.MAX_VALUE;
        for (int i = 0; i < 9; i++) {
          float dx = x - xs[i] * w, dy = y - ys[i] * h;
          float d = dx * dx + dy * dy;
          float hit = radius(i) * 1.8f;
          if (d <= hit * hit && d < best) { best = d; selected = i - 1; }
        }
        return true;
      }
      if (e.getActionMasked() == MotionEvent.ACTION_MOVE && selected >= -1) {
        int index = selected + 1;
        xs[index] = Math.max(0.055f, Math.min(0.945f, x / Math.max(1f, w)));
        ys[index] = Math.max(0.13f, Math.min(0.91f, y / Math.max(1f, h)));
        invalidate();
        return true;
      }
      if (e.getActionMasked() == MotionEvent.ACTION_UP || e.getActionMasked() == MotionEvent.ACTION_CANCEL) {
        if (selected >= -1) persist();
        selected = -2;
        return true;
      }
      return true;
    }

    private void finishActivity() { ((Activity)getContext()).finish(); }
  }
}
