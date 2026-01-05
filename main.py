import pandas as pd
import numpy as np
import sys

# --- הגדרות ---
INPUT_FILENAME = 'X_QAM16_20dB.csv'
OUTPUT_FILENAME = 'X_QAM16_20dB_hybrid.csv' # שם הקובץ החדש
RESOLUTION = 32  # מספר הביטים (אורך המחרוזת הבוליאנית)

def get_thermometer_strings(series, resolution):
    """
    מקבלת עמודת נתונים (כמו I או Q), מחשבת ספים לפי אחוזונים,
    ומחזירה רשימה של מחרוזות בוליאניות (למשל "11100").
    """
    # 1. חישוב ספים (Percentiles) לפי התפלגות הדאטה
    percentiles = np.linspace(0, 100, resolution + 2)[1:-1]
    thresholds = np.percentile(series, percentiles)
    
    # 2. יצירת מטריצה של ביטים בבת אחת (Broadcasting)
    # values: (N, 1), thresholds: (1, Resolution) -> result: (N, Resolution)
    values = series.values[:, None]
    threshs_row = thresholds[None, :]
    
    # השוואה: 1 אם הערך גדול מהסף, 0 אחרת
    bits_matrix = (values >= threshs_row).astype(int)
    
    # 3. המרה למחרוזות
    # אנו עוברים שורה-שורה ומחברים את המספרים לטקסט
    # הערה: זה עלול לקחת רגע אם הקובץ ענק, אבל ל-10K שורות זה מהיר מאוד
    str_list = ["".join(row.astype(str)) for row in bits_matrix]
    
    return str_list

def main():
    print(f"--- 1. טוען את הקובץ המקורי: {INPUT_FILENAME} ---")
    try:
        df_original = pd.read_csv(INPUT_FILENAME)
    except FileNotFoundError:
        print(f"שגיאה: הקובץ '{INPUT_FILENAME}' לא נמצא בתיקייה.")
        return

    # יצירת DataFrame חדש שירכז את התוצאות
    df_new = pd.DataFrame()

    print(f"--- 2. מבצע המרה (Quantile Binarization) למחרוזות... ---")

    # === טיפול ב-Q ===
    df_new['Q_Analog'] = df_original['Q']
    df_new['Q_Boolean'] = get_thermometer_strings(df_original['Q'], RESOLUTION)

    # === טיפול ב-I ===
    df_new['I_Analog'] = df_original['I']
    df_new['I_Boolean'] = get_thermometer_strings(df_original['I'], RESOLUTION)

    # === העתקת ה-Labels (התשובות) ===
    # חשוב מאוד שיהיו בקובץ כדי שהמכונה תדע מה היא לומדת
    labels = ['bit0', 'bit1', 'bit2', 'bit3']
    for col in labels:
        if col in df_original.columns:
            df_new[col] = df_original[col]

    # --- שמירה ---
    print(f"--- 3. שומר את הקובץ המעובד: {OUTPUT_FILENAME} ---")
    df_new.to_csv(OUTPUT_FILENAME, index=False)
    
    # --- הצגה למשתמש ---
    print("\nהתהליך הושלם! הנה דוגמה ל-5 השורות הראשונות בקובץ החדש:")
    print(df_new[['Q_Analog', 'Q_Boolean', 'I_Analog', 'I_Boolean']].head())

if __name__ == "__main__":
    main()