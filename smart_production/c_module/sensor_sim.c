/*
 * sensor_sim.c
 * AI-Based Smart Production Optimization System
 * Simulates industrial machine sensor data (mimics PLC/SCADA output).
 *
 * Compile : gcc sensor_sim.c -o sensor_sim -lm
 * Usage   : ./sensor_sim [num_records] [output_file.csv]
 * Default : ./sensor_sim 2000 ../data/sensor_data.csv
 */

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>
#include <string.h>

#define NUM_MACHINES  5
#define ANOMALY_RATE  0.08f
#define PI            3.14159265f

/* ── Baseline operating parameters per machine ─────────────────────────── */
static const float TEMP_BASE[NUM_MACHINES]    = {72.0f, 85.0f, 91.0f, 68.0f, 78.0f};
static const float VIBR_BASE[NUM_MACHINES]    = { 1.2f,  2.1f,  1.8f,  0.9f,  1.5f};
static const float PRESS_BASE[NUM_MACHINES]   = { 4.5f,  6.2f,  5.8f,  3.9f,  5.1f};
static const float CURRENT_BASE[NUM_MACHINES] = {12.0f, 18.5f, 15.0f, 10.5f, 14.0f};
static const float CYCLE_BASE[NUM_MACHINES]   = { 3.2f,  4.8f,  3.9f,  2.7f,  4.1f};
static const float OUTPUT_BASE[NUM_MACHINES]  = {110.f, 75.0f, 92.0f, 130.f, 88.0f};

static const char *MACHINE_NAMES[NUM_MACHINES] = {
    "CNC_Mill_A", "Lathe_B", "Press_C", "Conveyor_D", "Drill_E"
};
static const char *FACILITIES[NUM_MACHINES] = {
    "Plant_1", "Plant_1", "Plant_2", "Plant_2", "Plant_1"
};
static const char *FUNCTIONS[NUM_MACHINES] = {
    "Machining", "Machining", "Forming", "Assembly", "Machining"
};
static const char *PROCESSES[NUM_MACHINES] = {
    "CNC_Milling", "CNC_Turning", "Hydraulic_Press", "Material_Handling", "Drilling"
};
static const char *SPECIAL_PROCESSES[] = {
    "None", "Shot_Peening", "Heat_Treatment", "Anodizing",
    "Non_Destructive_Testing", "Welding", "Painting"
};

/* ── Data record ────────────────────────────────────────────────────────── */
typedef struct {
    float temperature;
    float vibration;
    float pressure;
    float current_draw;
    float cycle_time;
    float output_rate;
    int   fault_code;   /* 0=none 1=overheat 2=bearing 3=pressure 4=electrical */
} SensorReading;

/* ── Box-Muller normal distribution ────────────────────────────────────── */
float randf_normal(float mean, float stddev) {
    float u1 = (float)(rand() + 1) / ((float)RAND_MAX + 2.0f);
    float u2 = (float)(rand() + 1) / ((float)RAND_MAX + 2.0f);
    float z  = sqrtf(-2.0f * logf(u1)) * cosf(2.0f * PI * u2);
    return mean + z * stddev;
}

float clampf(float v, float lo, float hi) {
    return v < lo ? lo : (v > hi ? hi : v);
}

/* ── Fault injection (4 real-world failure modes) ───────────────────────── */
void inject_fault(SensorReading *r) {
    int t = rand() % 4;
    switch (t) {
        case 0: /* Overheating */
            r->temperature  *= randf_normal(1.35f, 0.05f);
            r->current_draw *= randf_normal(1.20f, 0.03f);
            r->fault_code    = 1; break;
        case 1: /* Bearing wear -> excessive vibration */
            r->vibration    *= randf_normal(2.80f, 0.15f);
            r->cycle_time   *= randf_normal(1.15f, 0.04f);
            r->output_rate  *= randf_normal(0.78f, 0.05f);
            r->fault_code    = 2; break;
        case 2: /* Pressure drop */
            r->pressure     *= randf_normal(0.55f, 0.06f);
            r->output_rate  *= randf_normal(0.85f, 0.04f);
            r->fault_code    = 3; break;
        case 3: /* Electrical surge */
            r->current_draw *= randf_normal(1.60f, 0.08f);
            r->temperature  *= randf_normal(1.18f, 0.04f);
            r->output_rate  *= randf_normal(0.70f, 0.06f);
            r->fault_code    = 4; break;
    }
}

/* ── Timestamp: simulate 5-min intervals from a fixed epoch ────────────── */
void make_timestamp(char *buf, size_t sz, int index) {
    time_t base = 1700000000 + (time_t)index * 300;
    struct tm *t = gmtime(&base);
    strftime(buf, sz, "%Y-%m-%d %H:%M:%S", t);
}

/* ── Main ───────────────────────────────────────────────────────────────── */
int main(int argc, char *argv[]) {
    int  num_records = 2000;
    char outfile[256] = "../data/sensor_data.csv";

    if (argc >= 2) num_records = atoi(argv[1]);
    if (argc >= 3) strncpy(outfile, argv[2], 255);

    srand((unsigned int)time(NULL));

    FILE *fp = fopen(outfile, "w");
    if (!fp) {
        fprintf(stderr, "ERROR: Cannot open '%s' for writing.\n", outfile);
        fprintf(stderr, "TIP : Run from c_module/ or create the data/ directory first.\n");
        return 1;
    }

    /* CSV header -- must match data_loader.py FEATURE_COLS */
    fprintf(fp, "timestamp,machine_id,machine_name,facility,function,process,special_process,batch_id,"
                "temperature_c,vibration_mms,pressure_bar,"
                "current_a,cycle_time_s,output_rate_uph,"
                "fault_code,fault_flag\n");

    printf("[sensor_sim] Writing %d records to %s ...\n", num_records, outfile);

    int faults = 0;
    for (int i = 0; i < num_records; i++) {
        int mid = rand() % NUM_MACHINES;

        SensorReading r;
        r.fault_code   = 0;
        r.temperature  = randf_normal(TEMP_BASE[mid],    TEMP_BASE[mid]    * 0.03f);
        r.vibration    = randf_normal(VIBR_BASE[mid],    VIBR_BASE[mid]    * 0.05f);
        r.pressure     = randf_normal(PRESS_BASE[mid],   PRESS_BASE[mid]   * 0.04f);
        r.current_draw = randf_normal(CURRENT_BASE[mid], CURRENT_BASE[mid] * 0.03f);
        r.cycle_time   = randf_normal(CYCLE_BASE[mid],   CYCLE_BASE[mid]   * 0.04f);
        r.output_rate  = randf_normal(OUTPUT_BASE[mid],  OUTPUT_BASE[mid]  * 0.05f);

        /* Clamp to physically plausible sensor ranges */
        r.temperature  = clampf(r.temperature,  20.0f, 200.0f);
        r.vibration    = clampf(r.vibration,     0.1f,  30.0f);
        r.pressure     = clampf(r.pressure,      0.5f,  20.0f);
        r.current_draw = clampf(r.current_draw,  1.0f,  60.0f);
        r.cycle_time   = clampf(r.cycle_time,    0.5f,  30.0f);
        r.output_rate  = clampf(r.output_rate,   5.0f, 300.0f);

        if ((float)rand() / RAND_MAX < ANOMALY_RATE) {
            inject_fault(&r);
            faults++;
        }

        char ts[24];
        make_timestamp(ts, sizeof(ts), i);

        const char *special = SPECIAL_PROCESSES[i % 7];
        fprintf(fp, "%s,%d,%s,%s,%s,%s,%s,B-%04d,%.2f,%.3f,%.3f,%.3f,%.3f,%.2f,%d,%d\n",
                ts, mid, MACHINE_NAMES[mid],
                FACILITIES[mid], FUNCTIONS[mid], PROCESSES[mid], special, (i / 20) + 1,
                r.temperature, r.vibration, r.pressure,
                r.current_draw, r.cycle_time, r.output_rate,
                r.fault_code, (r.fault_code > 0) ? 1 : 0);
    }

    fclose(fp);
    printf("[sensor_sim] Done. Records: %d | Faults injected: %d (%.1f%%)\n",
           num_records, faults, 100.0f * faults / num_records);
    return 0;
}
