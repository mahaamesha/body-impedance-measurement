/*
	ad5933-test
	Reads impedance values from the AD5933 over I2C and prints them serially.
*/

#include <Wire.h>
#include <AD5933.h>
#include <cmath>
#include <bits/stdc++.h>	// for function: sort()
 
using namespace std;

#define START_FREQ  (20000)
#define FREQ_INCR   (1000)
#define NUM_INCR    (30)
#define REF_RESIST  (1008)

double gain[NUM_INCR+1];	// should double
int phase[NUM_INCR+1];

bool cal_flag = 1;	// testing, set it to TRUE
bool mux_flag = 1;	// select ch1/2

// define pin here			// ch0	-> (S2,S1,S0) = (0,0,0)
int PIN_S0 = 32;			// ch1	-> (S2,S1,S0) = (0,0,1)
int PIN_S1 = 33;			// ch2	-> (S2,S1,S0) = (0,1,0)

// define struct here
// struct to store internal factor
struct struct_internal_factor {
	int z_cal = REF_RESIST;
	int phase_cal = 0;
	float delta_z[NUM_INCR];
	float delta_phase[NUM_INCR];
} internal_factor;


// store data from measurement in array. for each parameter
struct struct_data {
	// data from measurement
	float freq[NUM_INCR];
	float impedance[NUM_INCR];
	float phase[NUM_INCR];
	
	float actual_impedance[NUM_INCR];
	float actual_phase[NUM_INCR];

	// data from statistics
	float f_mid;
	float z_mid;
	float phase_mid;
	float r_mid;
	float c_mid;
} data_retrieval;


// store data of body composition
struct struct_body_composition {
	int weight;
	int height;
	int age;
	int gender;

	float impedance;
	float ffm;
	float ffm_percentage;
	float fm;
	float fm_percentage;
	float tbw;
	float tbw_percentage;
} body_composition;


// define function here
void check_inizialization_ad5933();
void change_pin_condition(int PIN_S0, int PIN_S1);
void set_pinmode(int PIN_S0, int PIN_S1);
float calculate_phase(int real, int imag);
void store_sampling(int freq, float impedance, float phase, struct_data *data, int idx);
void consider_internal_factor(struct_data *data, struct_internal_factor *internal, int idx);
float get_data_mid(float arr[], int length);
float get_data_median(float arr[], int length);
float calculate_r(float z, float phase);
float calculate_c(float z, float phase, float f);
float calculate_ffm(int w, int h, float z, int y, int s);
float calculate_fm(int w, float ffm);
float calculate_tbw(float ffm, float percentage);
float calculate_percentage(float ref, float value);
void process_analysis(struct_data *data, struct_body_composition *body);
void debug_print();
void frequency_sweep_easy();
void frequency_sweep_real_time();


void setup() {
	// Begin I2C
	Wire.begin();

	// Begin serial at 9600 baud for output
	Serial.begin(9600);
	Serial.println("AD5933 Test Started!");

	// set pinmode here
	set_pinmode(PIN_S0, PIN_S1);

	// Perform initial configuration. Fail if any one of these fail.
	if (!(AD5933::reset() &&
		AD5933::setInternalClock(true) &&
		AD5933::setStartFrequency(START_FREQ) &&
		AD5933::setIncrementFrequency(FREQ_INCR) &&
		AD5933::setNumberIncrements(NUM_INCR) &&
		AD5933::setPGAGain(PGA_GAIN_X1))) {
			Serial.println("FAILED in initialization!");
			check_inizialization_ad5933();
			while (true);	// if its failed, infinite loop
	}

	// Perform calibration sweep
	if (AD5933::calibrate(gain, phase, REF_RESIST, NUM_INCR+1)) {
		// in calibration process, i need to store first sweep data using RCAL
		// i want to store it to struct internal_factor
		frequency_sweep_real_time();	// in the end, cal_flag will changed to 0
		Serial.println("Calibrated!\n");
	}
	else {
		Serial.println("Calibration failed...\n");
	}
}

void loop() {
	// ask input anthropometry data
	input_anthropometry(&body_composition);

	// Easy to use method for frequency sweep
	// frequency_sweep_easy();

	// Complex but more robust method for frequency sweep
	frequency_sweep_real_time();

	// process analysis
	// internal factor and model need to stored when calibration


	delay(500);
}


// source of function is here
void check_inizialization_ad5933() {
	if (! AD5933::reset()) Serial.println("Failed: Reset AD5933");
	if (! AD5933::setInternalClock(true)) Serial.println("Failed: Set internal clock");
	if (! AD5933::setStartFrequency(START_FREQ)) Serial.println("Failed: Set start frequency");
	if (! AD5933::setIncrementFrequency(FREQ_INCR)) Serial.println("Failed: Set increment frequency");
	if (! AD5933::setNumberIncrements(NUM_INCR)) Serial.println("Failed: Set number increment");
	if (! AD5933::setPGAGain(PGA_GAIN_X1)) Serial.println("Failed: Set PGA Gain x1");
}


// setting pin S0 S1 condition
void change_pin_condition(int PIN_S0, int PIN_S1) {
	// mux_flag chose channel 1 or channel 2
	if (mux_flag && !cal_flag) {		// for ch 1
		digitalWrite(PIN_S0, HIGH);
		digitalWrite(PIN_S1, LOW);
	}
	else if (!mux_flag && !cal_flag) {	// for ch 2
		digitalWrite(PIN_S0, LOW);
		digitalWrite(PIN_S1, HIGH);
	}
	else if (cal_flag) {				// for ch 0 -> calibration
		digitalWrite(PIN_S0, LOW);
		digitalWrite(PIN_S1, LOW);
	}
}


// setting pinmode in setup
void set_pinmode(int PIN_S0, int PIN_S1) {
	pinMode(PIN_S0, OUTPUT);
	pinMode(PIN_S1, OUTPUT);
	change_pin_condition(PIN_S0, PIN_S1);
}


// input anthropometry data
// change this function when mobile app already builded
void input_anthropometry(struct_body_composition *body) {
	(*body).weight = 57;		// default value for testing
	(*body).height = 169;		// later I will ask input from application
	(*body).age = 21;
	(*body).gender = 1;
}


// to calculate phase related to its quadrant position
float calculate_phase(int real, int imag) {
	float phase;
	if (real > 0 && imag > 0) phase = atan(imag/real) * 180 / M_PI;
	else if (real < 0 && imag > 0) phase = atan(imag/real) * 180 / M_PI + 180;
	else if (real < 0 && imag < 0) phase = atan(imag/real) * 180 / M_PI + 180;
	else if (real > 0 && imag < 0) phase = atan(imag/real) * 180 / M_PI + 360;

	return phase;
}


// i store data to struct_sampling to get minimal parameter in other function
void store_sampling(int freq, float impedance, float phase, struct_data *data, int idx) {
	(*data).freq[idx] = freq;
	(*data).impedance[idx] = impedance;
	(*data).phase[idx] = phase;
}


// in calibration process, z_cal and phase_cal stored in struct_data first.
// so, i need to calculate 
void store_internal_factor(float impedance, float phase, struct_internal_factor *internal, int idx) {
	(*internal).delta_z[idx] = impedance - (*internal).z_cal;
	(*internal).delta_phase[idx] = phase - (*internal).phase_cal;
}


// consider internal factor by substract the value of data
// similar to creata_actual_params_columns() in processing.py
void consider_internal_factor(struct_data *data, struct_internal_factor *internal, int idx) {
	(*data).actual_impedance[idx] = (*data).impedance[idx] - (*internal).delta_z[idx];
	(*data).actual_phase[idx] = (*data).phase[idx] - (*internal).delta_phase[idx];
}


// use this to get data in fmid
float get_data_mid(float arr[], int length) {
	int idx = floor((length-1)/2);
	float mid = arr[idx];

	return mid;
}


// use this to get median data
float get_data_median(float arr[], int length) {
    // first we sort the array
    sort(arr, arr + length);		// from #include <bits/stdc++.h>
 
    // if odd
    if (length % 2 != 0) 
		return (float)arr[length/2];
	
	// if even. sum it, then divide by 2
    return (float)(arr[(length-1)/2] + arr[length/2]) / 2.0;
}


float calculate_r(float z, float phase) {
	phase *= M_PI / 180;	// convert to radian
	float param = 1 + pow(tan(phase), 2);
	float r = z * sqrt(param);
	return r;
}


float calculate_c(float z, float phase, float f) {
	phase *= M_PI / 180;	// convert to radian
	float param;
	if (abs(phase) == 0)
		param = INFINITY;
	else
		param = 1 + 1/pow(tan(phase), 2);
	float c = 1 / ( 2 * M_PI * f * z * sqrt(param) );
	return c;
}


// to calculate fat-free mass
float calculate_ffm(int w, int h, float z, int y, int s) {
	// Predicting body composition using foot-to-foot bioelectrical impedance analysis in healthy Asian individuals
    // https://www.researchgate.net/publication/277088052_Predicting_body_composition_using_foot-to-foot_bioelectrical_impedance_analysis_in_healthy_Asian_individuals#:~:text=13.055%20%2B%200.204%20w,y%20%2B%208.125%20S
    // w : weight (kg)
    // h : heigth (cm)
    // z : impedance (ohm)
    // y : age (years)
    // s : gender (male=1, female=0)
    float ffm_kg = 13.055 + 0.204*w + 0.394*(h*h)/z - 0.136*y + 8.125*s;
	return ffm_kg;
}


// to calculate fat mass
float calculate_fm(int w, float ffm) {
	float fm_kg = w - ffm;
    return fm_kg;
}


// to calculate total body water
float calculate_tbw(float ffm, float percentage=0.73) {
	// NIHR | Cambridge Biomedical Research Centre
    // https://dapa-toolkit.mrc.ac.uk/anthropometry/objective-methods/bioelectric-impedence-analysis#:~:text=FFM)%2C%20assuming%20that-,73,-%25%20of%20the%20body%E2%80%99s
    float tbw_kg = ffm * percentage;
    return tbw_kg;
}


float calculate_percentage(float ref, float value) {
    float percentage = value / ref * 100;
    return percentage;
}


void process_analysis(struct_data *data, struct_body_composition *body) {
	// get median data
	(*data).f_mid = get_data_median((*data).freq, NUM_INCR);
	(*data).z_mid = get_data_median((*data).actual_impedance, NUM_INCR);
	(*data).phase_mid = get_data_median((*data).actual_phase, NUM_INCR);
	
	// calculate r and c value
	(*data).r_mid = calculate_r((*data).z_mid, (*data).phase_mid);
	(*data).c_mid = calculate_c((*data).z_mid, (*data).phase_mid, (*data).f_mid);

	// update impedance value from data z_mid
	(*body).impedance = (*data).z_mid;

	// calculate body composition in kg & percentage unit
	int w = (*body).weight;
	int h = (*body).height;
	int y = (*body).age;
	int s = (*body).gender;
	float z = (*body).impedance;
	
	(*body).ffm = calculate_ffm(w, h, z, y, s);
	(*body).fm = calculate_fm(w, (*body).ffm);
    (*body).tbw = calculate_tbw((*body).ffm);

	(*body).ffm_percentage = calculate_percentage(w, (*body).ffm);
    (*body).fm_percentage = calculate_percentage(w, (*body).fm);
    (*body).tbw_percentage = calculate_percentage(w, (*body).tbw);
}


void debug_print() {
	cout << "f_mid (hz)        :" << data_retrieval.f_mid << "\n";
	cout << "z_mid (ohm)       :" << data_retrieval.z_mid << "\n";
	cout << "phase_mid (degree):" << data_retrieval.phase_mid << "\n";
	cout << "r_mid (ohm)       :" << data_retrieval.r_mid << "\n";
	cout << "c_mid (farad)     :" << data_retrieval.c_mid << "\n";

	cout << "w (kg)  :" << body_composition.weight << "\n";
	cout << "h (cm)  :" << body_composition.height << "\n";
	cout << "y (yo)  :" << body_composition.age << "\n";
	cout << "s (1/0) :" << body_composition.gender << "\n";
	cout << "z (ohm) :" << body_composition.impedance << "\n";
	cout << "ffm (kg):" << body_composition.ffm << "\n";
	cout << "ffm (%) :" << body_composition.ffm_percentage << "\n";
	cout << "fm (kg) :" << body_composition.fm << "\n";
	cout << "fm (%)  :" << body_composition.fm_percentage << "\n";
	cout << "tbw (kg):" << body_composition.tbw << "\n";
	cout << "tbw (%) :" << body_composition.tbw_percentage << "\n";

	delay(3000);
}


// Removes the frequencySweep abstraction from above. This saves memory and
// allows for data to be processed in real time. However, it's more complex.
void frequency_sweep_real_time() {
	// Create variables to hold the impedance data and track frequency
	int real, imag, i = 0, cfreq = START_FREQ;

	// Initialize the frequency sweep
	if (!(AD5933::setPowerMode(POWER_STANDBY) &&          // place in standby
		AD5933::setControlMode(CTRL_INIT_START_FREQ) && // init start freq
		AD5933::setControlMode(CTRL_START_FREQ_SWEEP))) // begin frequency sweep
		{
			Serial.println("Could not initialize frequency sweep...");
		}

	// print what next to do
	// Serial.println("Sweep frequency ... ");
	// Perform the actual sweep
	while ((AD5933::readStatusRegister() & STATUS_SWEEP_DONE) != STATUS_SWEEP_DONE) {
		// Get the frequency data for this frequency point
		if (!AD5933::getComplexData(&real, &imag)) {
			Serial.println("Could not get raw frequency data...");
		}

		// Compute impedance
		float magnitude = sqrt(pow(real, 2) + pow(imag, 2));
		float impedance = 1/(magnitude*gain[i]);
		float phase = calculate_phase(real, imag);
		
		// if in calibration process
		if (cal_flag) {
			// in calibration process, i need to store delta_z & delta_phase
			store_internal_factor(impedance, phase, &internal_factor, i);

			// Print out the frequency data
			Serial.print(cfreq);
			Serial.print(", ");
			Serial.print(internal_factor.delta_z[i]);
			Serial.print(", ");
			Serial.println(internal_factor.delta_phase[i]);
		}
		else {		// if in measurement mode
			// store to struct
			store_sampling(cfreq, impedance, phase, &data_retrieval, i);
			// get actual value, considering internal factor
			consider_internal_factor(&data_retrieval, &internal_factor, i);

			// Print out the frequency data
			// i dont need to change print variable using corrected value from data_retrieval
			// cause this will be used in collecting data for training process
			// corrected value used in process_analysis()
			Serial.print(cfreq);
			Serial.print(", ");
			Serial.print(impedance);
			Serial.print(", ");
			Serial.print(phase);
			Serial.print(", ");
			Serial.print(real);
			Serial.print(", ");
			Serial.print(imag);
			Serial.print(", ");
			Serial.println(magnitude);
		}

		// Increment the frequency
		i++;
		cfreq += FREQ_INCR;
		AD5933::setControlMode(CTRL_INCREMENT_FREQ);
	}

	
	// process analysis here
	if (cal_flag) {
		Serial.println("Sweep frequency & store internal factor ... Done");
		cal_flag = 0;
	}
	else {
		Serial.println("Frequency sweep complete!");
		process_analysis(&data_retrieval, &body_composition);
		// debug_print();
	}


	// Set AD5933 power mode to standby when finished
	if (!AD5933::setPowerMode(POWER_STANDBY))
		Serial.println("Could not set to standby...");
}