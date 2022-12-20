//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~//
// Execution Controls
//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~//
// 146.139.66.5 = testing
// 146.139.66.9 = production
#define ATLAS_IP				"146.139.66.9"

// Show Debug Information
const bool G_bDebug = true;

// Perform specific testing using TestingCode()
const bool G_bTesting = true;


//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~//
// Defines
//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~//
#define MAX_CUPS				20
#define TRUE					1
#define SUCCESS					1
#define FALSE					0
#define FAILURE					0

#define USER_MESSAGE_LENGTH		1024
#define CHANNEL_NAME_MAX		80
#define FC_NAME_LENGTH			16
#define SOURCE_NAME_LENGTH		8
#define BEAMLINE_ABR_LENGTH		8
#define EXP_NAME_LENGTH			32
#define ATTEN_STR_LENGTH		16
#define USER_INPUT_LENGTH		16
#define SLITS_STR_LENGTH		40
#define NUM_SLITS				26

#define NUM_CUP_READINGS		6

#define ECR1_FC					"FCP001"
#define ECR2_FC					"FCR001"
#define ECR3_FC					"FCP201"
#define PII_ENTRANCE_FC			"FCP202"
#define	PII_EXIT_FC				"FCP301"
#define ATTENUATION_FC			"FCP302"
#define	BOOSTER_ENTRANCE_FC		"FCP303"
#define	BOOSTER_EXIT_FC			"FCB000"
#define	ATLAS_ENTRANCE_FC		"FCB201"
#define ATLAS_EXIT_FC			"FCA001"
#define TOF_FC					"FCA004"

#define	SLIT_VDB				"SLIT_CTL_VDB"
#define RAISOR_SLIT_VDB			"RAISOR_STEPPER_VDB"
#define SLIT_NAME_2JF101_L		"LEFT_2JF101"
#define SLIT_NAME_2JF101_R		"RIGHT_2JF101"
#define SLIT_NAME_4JR001_L		"LEFT_4JR001"
#define SLIT_NAME_4JR001_R		"RIGHT_4JR001"
#define SLIT_NAME_4JR001_T		"TOP_4JR001"
#define SLIT_NAME_4JR001_B		"BOTTOM_4JR001"
#define SLIT_NAME_2JR101_L		"LEFT_2JR101"
#define SLIT_NAME_2JR101_R		"RIGHT_2JR101"
#define SLIT_NAME_2JP001_L		"LEFT_2JP001"
#define SLIT_NAME_2JP001_R		"RIGHT_2JP001"
#define SLIT_NAME_2JP101_L		"LEFT_2JP101"
#define SLIT_NAME_2JP101_R		"RIGHT_2JP101"
#define SLIT_NAME_4JG101_L		"LEFT_4JG101"
#define SLIT_NAME_4JG101_R		"RIGHT_4JG101"
#define SLIT_NAME_4JG101_T		"TOP_4JG101"
#define SLIT_NAME_4JG101_B		"BOTTOM_4JG101"
#define SLIT_NAME_2JP201_L		"LEFT_2JP201"
#define SLIT_NAME_2JP201_R		"RIGHT_2JP201"
#define SLIT_NAME_2JP302_T		"TOP_2JP302"
#define SLIT_NAME_2JP302_B		"BOTTOM_2JP302"
#define SLIT_NAME_2JB101_L		"LEFT_2JB101"
#define SLIT_NAME_2JB101_R		"RIGHT_2JB101"
#define RAISOR_LEFT_SLIT		"MOTOR_1_CURRENT_ENCODER_POSITION"
#define RAISOR_RIGHT_SLIT		"MOTOR_4_CURRENT_ENCODER_POSITION"
#define RAISOR_TOP_SLIT			"MOTOR_5_CURRENT_ENCODER_POSITION"
#define RAISOR_BOTTOM_SLIT		"MOTOR_3_CURRENT_ENCODER_POSITION"

// Multiplexor 107 channels [1] and [2], respectively
#define ANALOG_METER			1
#define DIGITAL_METER			2

// Address for the digital keithley server
#define KEITHLEY_IP				"146.139.66.23"

// Address for the RAISOR slits & AMIS database
#define ATLAS83_IP				"146.139.66.83"

// Location for csv file in server
#define CSV_FILE_PATH			"DISK$ATLAS:[PROGRAMS.READ_FARADAY_CUPS]AFC_READINGS.CSV"

// Source IDs
#define ECR1_NAME				"ECR1"
#define ECR2_NAME				"ECR2"
#define ECR3_NAME				"ECR3"
#define SOURCE_ECR1				0
#define SOURCE_ECR2				1
#define SOURCE_ECR3				2


//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~//
// TestingCode()
//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~//
#define NAME_LENGTH			40
#define OUTPUT_LENGTH		30
#define MAXIMUM_REQUESTS	100
#define CSV_TEST_PATH		"DISK$ATLAS:[PROGRAMS.READ_FARADAY_CUPS]AFC_LOGGER.CSV"

// Database Names
#define FC_VDB				"FC_VDB"
#define STEPPER_MOTOR_VDB	"STEPPER_MOTOR_VDB"
#define STATUS_DISPLAY_VDB	"STATUS_DISPLAY_VDB"
#define RAISOR_VDB			"RAISOR_VDB"
#define PARAMS_VDB			"PARAMS_VDB"
#define SWITCH_VDB			"SWITCH_VDB"
#define ECR2_VDB			"ECR_2_VDB"
#define SOL_VDB				"SOL_VDB"
#define TOF_VDB				"TOF_VDB"
#define GUIDE_VDB			"GUIDE_VDB"
#define GAUSS_VDB			"GAUSS_VDB"
#define AMIS_VDB			"AMIS_VDB"

// Dynamic variables
char G_csTarget[CHANNEL_NAME_MAX];		// Location of desired value
char G_csServerName[NAME_LENGTH];		// Server address
char G_csDatabaseName[NAME_LENGTH];		// Database name
bool G_bString =		false;
bool G_bVacuum =		false;


//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~//
// Global Variables
//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~//
char G_csChannelName[CHANNEL_NAME_MAX + 1];
char G_csMessage[USER_MESSAGE_LENGTH];		// Final output message to user
char G_csTempMessage[USER_MESSAGE_LENGTH];	// String to append to the final output
char G_csDefaultCup[FC_NAME_LENGTH]; 		// Cup to put in when complete or error
char G_csBackupCup[FC_NAME_LENGTH];			// Backup cup for all sources
char G_csBeamline[BEAMLINE_ABR_LENGTH];		// Global beamline abbreviation
char G_csSourceName[SOURCE_NAME_LENGTH];	// Global source abbreviation
char G_csExperimentNumber[EXP_NAME_LENGTH];	// Global experiment number
char G_csAttenuation[ATTEN_STR_LENGTH];		// Global attenuation sum
char G_csUserInput[USER_INPUT_LENGTH];		// Global FC stopping cup
float	G_fSlits[NUM_SLITS];				// Global array for slits
long	G_lAST_ID;
bool	G_bRequestToExit = false;	// Users request to exit
bool	G_bCSV = false;				// Status of CSV file
float	G_fZero = 0.0;				// Zero
float	G_fFail = -0.000000001;		// Failed cup shows -1.000enA
double	G_dZero = 0.0;				// Zero
int		G_iSourceID;				// Integer to identify source
time_t	G_t;
struct	tm *timeinfo;
timeinfo = localtime(&G_t);

vista_chix G_chixUserMessageDisplay;
vista_chix G_chixBeamMeasTimeStamp;
vista_chix G_chixKeithleyReadMonitor;
vista_chix G_chixKeithleyInitialize;
vista_chix G_chixAnalogMUXMeter;
vista_chix G_chixDigitalMUXMeter;

FILE *fpt;

// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

int DetermineSlits(void)
{
  // Slit information is hard-coded in DetermineSlits() and main() !!!!!
  
  vista_chix slits_chix;
  char csTempName[SLITS_STR_LENGTH];	// Holds the varying slit name
  float fTempPosition;					// Holds the varying slit position
  int iIndex = 0;

  if ( G_bDebug )
  {
	printf("Read_Faraday_Cups -- DetermineSlits() begins...\n");
  }

  // Loop through the slits for this beampath
  // Retrieve the slit position and write it to the array
  for (iIndex = 0; iIndex < NUM_SLITS; iIndex++)
  {
	// Switch for everything at this time
	switch ( iIndex )
	{
	  // 2JF101
	  case (0):
		strcpy(csTempName, SLIT_NAME_2JF101_L);
		break;
	  case (1):
		strcpy(csTempName, SLIT_NAME_2JF101_R);
		break;
	  
	  // 4JR001
	  case (2):
		strcpy(csTempName, SLIT_NAME_4JR001_L);
		break;
	  case (3):
		strcpy(csTempName, SLIT_NAME_4JR001_R);
		break;
	  case (4):
		strcpy(csTempName, SLIT_NAME_4JR001_T);
		break;
	  case (5):
		strcpy(csTempName, SLIT_NAME_4JR001_B);
		break;
	  
	  // 2JR101
	  case (6):
		strcpy(csTempName, SLIT_NAME_2JR101_L);
		break;
	  case (7):
		strcpy(csTempName, SLIT_NAME_2JR101_R);
		break;
	  
	  // 2JP001
	  case (8):
		strcpy(csTempName, SLIT_NAME_2JP001_L);
		break;
	  case (9):
		strcpy(csTempName, SLIT_NAME_2JP001_R);
		break;
	  
	  // 2JP101
	  case (10):
		strcpy(csTempName, SLIT_NAME_2JP101_L);
		break;
	  case (11):
		strcpy(csTempName, SLIT_NAME_2JP101_R);
		break;
	  
	  // 4JG101
	  case (12):
		strcpy(csTempName, SLIT_NAME_4JG101_L);
		break;
	  case (13):
		strcpy(csTempName, SLIT_NAME_4JG101_R);
		break;
	  case (14):
		strcpy(csTempName, SLIT_NAME_4JG101_T);
		break;
	  case (15):
		strcpy(csTempName, SLIT_NAME_4JG101_B);
		break;
	  
	  // 2JP201
	  case (16):
		strcpy(csTempName, SLIT_NAME_2JP201_L);
		break;
	  case (17):
		strcpy(csTempName, SLIT_NAME_2JP201_R);
		break;
	  
	  // 2JP302
	  case (18):
		strcpy(csTempName, SLIT_NAME_2JP302_T);
		break;
	  case (19):
		strcpy(csTempName, SLIT_NAME_2JP302_B);
		break;
	  
	  // 2JB101
	  case (20):
		strcpy(csTempName, SLIT_NAME_2JB101_L);
		break;
	  case (21):
		strcpy(csTempName, SLIT_NAME_2JB101_R);
		break;
		
	  // RAISOR
	  case (22):
		strcpy(csTempName, RAISOR_LEFT_SLIT);
		break;
	  case (23):
		strcpy(csTempName, RAISOR_RIGHT_SLIT);
		break;
	  case (24):
		strcpy(csTempName, RAISOR_TOP_SLIT);
		break;
	  case (25):
		strcpy(csTempName, RAISOR_BOTTOM_SLIT);
		break;
	}
	
	// Create the channel name with the given slit name
	if ( iIndex < 22)
	{
	  snprintf(G_csChannelName, CHANNEL_NAME_MAX, "\\\\%s\\%s::%s:MONITOR",
				ATLAS_IP, SLIT_VDB, csTempName);
	}
	else
	{
	  // RAISOR slits are located on ATLAS83
	  snprintf(G_csChannelName, CHANNEL_NAME_MAX, "\\\\%s\\%s::%s:MONITOR",
				ATLAS83_IP, RAISOR_SLIT_VDB, csTempName);
	}

	// Get the slit chix
	if (!(vdbc_channel_index(G_csChannelName, &slits_chix)))
	{
	  vdb_error_handling_routine(slits_chix, G_csChannelName);
	  return (FAILURE);
	}

	// Get the slit position
	if (!(vdb_rget(&slits_chix, &fTempPosition)))
	{
	  vdbc_channel_name(&slits_chix, G_csChannelName, CHANNEL_NAME_MAX);
	  vdb_error_handling_routine(slits_chix, G_csChannelName);
	  return (FAILURE);
	}

	// Write the slit position to array
	G_fSlits[iIndex] = fTempPosition;

  }
  // End of for loop

  return (SUCCESS);
}

// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

// ....

	// Add slits based on source
	if ( G_iSourceID == SOURCE_ECR1 )
	{
	  fprintf(fpt, "\n2JP001 L/R = [%.2f/%.2f]", G_fSlits[8], G_fSlits[9]);
	  fprintf(fpt, "\n2JP101 L/R = [%.2f/%.2f]", G_fSlits[10], G_fSlits[11]);
	}
	else if ( G_iSourceID == SOURCE_ECR2 )
	{
	  fprintf(fpt, "\n2JF101 L/R = [%.2f/%.2f]", G_fSlits[0], G_fSlits[1]);
	  fprintf(fpt, "\n4JR001 L/R/T/B = [%.2f/%.2f/%.2f/%.2f]", G_fSlits[2], G_fSlits[3], G_fSlits[4], G_fSlits[5]);
	  fprintf(fpt, "\n2JR101 L/R = [%.2f/%.2f]", G_fSlits[6], G_fSlits[7]);
	  fprintf(fpt, "\n2JP101 L/R = [%.2f/%.2f]", G_fSlits[10], G_fSlits[11]);
	}
	else if ( G_iSourceID == SOURCE_ECR3 )
	{
	  fprintf(fpt, "\n4JG101 L/R/T/B = [%.2f/%.2f/%.2f/%.2f]", G_fSlits[12], G_fSlits[13], G_fSlits[14], G_fSlits[15]);
	}

	// All target areas include 2JP201
	fprintf(fpt, "\n2JP201 L/R = [%.2f/%.2f]", G_fSlits[16], G_fSlits[17]);

	// Check target areas to determine approriate slits
	if (!strncmp(G_csBeamline, "P4", BEAMLINE_ABR_LENGTH))
	{
		// No more slits to add
		;
	}
	else
	{
		// Add 2JP302 since we are beyond AMIS
		fprintf(fpt, "\n2JP302 T/B = [%.2f/%.2f]", G_fSlits[18], G_fSlits[19]);
	
		// Check if the target area is AREA II
		if (	(!strncmp(G_csBeamline, "P4", BEAMLINE_ABR_LENGTH)) ||
				(!strncmp(G_csBeamline, "B4", BEAMLINE_ABR_LENGTH)) ||
				(!strncmp(G_csBeamline, "B5", BEAMLINE_ABR_LENGTH)) )
		{
			// No more slits to add
			;
		}
		else
		{
			fprintf(fpt, "\n2JB101 L/R = [%.2f/%.2f]", G_fSlits[20], G_fSlits[21]);
			fprintf(fpt, "\nRAISOR L/R/T/B = [%.3f/%.3f/%.3f/%.3f]", G_fSlits[22], G_fSlits[23], G_fSlits[24], G_fSlits[25]);
		}
	}	

// ....