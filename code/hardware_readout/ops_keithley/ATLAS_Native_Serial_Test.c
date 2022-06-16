
//    Function Name:          ATLAS_Native_Serial_Test
//    Directory Name:
//    File Name:              ATLAS_Native_Serial_Test.c
//
//    Associated Files:
//
//    Linking Procedure:
//
//    Related Documents:
//    
//    Installation:           Argonne National Laboratory
//                          Physics Division
//                          ATLAS Facility
//
//    Author(s):              J. Dreher (C. Peters)
//    Date:                   12-Feb-2013
//
//    Revisions:
//
//    Description:            This is the test component for the 
//                          ATLAS_Native_Serial_Handlers library.
//
//    Notes(s):               
//*******************************************************************************

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "ATLAS_Native_Generic_Serial.h"

#define SGXPORTNUMBER        1
#define SGYPORTNUMBER        3

char G_csUSBPortNumber[255];
char G_csAddress[255];
char G_csIgnoreNewlines[255];
char G_csBlockFlag[255];
char G_csBaudRate[255];
char G_csParity[255];
char G_csBits[255];
char G_csStopBits[255];
char G_csSlaveNumber[255];
char G_csRegisterNumber[255];
char G_csTerminationOption[255];

int G_iUSBPortNumber;
int G_iBaudRate;
int G_iParity;
int G_iBits;
int G_iStopBits;
int G_iBlockFlag;
int G_iIgnoreNewlines;
int G_iSlaveNumber;
int G_iRegisterNumber;
int G_iTerminationOption;

int main(int argc, char** argv) 
{
    int iReturn = SUCCESS;

    char csCommand[MAXCOMMANDSIZE];
    char csVoltage[MAXCOMMANDSIZE];
    char csMode[2];
    char csPosition[MAXCOMMANDSIZE];
    char csQueryString[MAXCOMMANDSIZE];
    char csDisplayString[MAXCOMMANDSIZE];
    char csRateSetting[3];
    char csReadBuffer[MAXLENGTH];
    char cMenuSelection[4];

    char cRegisterID;
    int iRegisterID; //used to convert char to at
 
    int  iHparams[22];
    int  iNumParams;
    int  iFunction;
    int  iAddress;
    int  iNumValues;
    int  iData = 0;
    int  iTestSelectionID;
    int  iCommandID;

    int  iRLCommandID;

    int  iNeedToSetFlag = 0;
    int  iWriteLength;
    int  iReadLength;
    int  iNumBytesRead = 0;
    int  iWaitTime = 0;

    // Looping Variables
    int iMinValue;
    int iMaxValue;
    int iIndex;

    float fData = 0.0;

    char    bStopFlag;

    int iSwitchPosition;
    int iNumData;
    
    while (iTestSelectionID != 99)
    {

        printf("MAIN MENU - Please enter your test selection (99-Exit) (#): \n");
        printf("\t1 - Test ATLAS_Native_Generic_Serial\n");
        
        fgets(cMenuSelection, sizeof (cMenuSelection), stdin);
        sscanf(cMenuSelection, "%i", &iTestSelectionID); //With extra space
       
        if (0 == iNeedToSetFlag && iTestSelectionID != 98 && iTestSelectionID != 99)
        {
            printf("Need to set port number before doing test.\n");
            printf("Redirecting to option 98 (Set Port Number)...\n");
            iTestSelectionID = 98;
        }
        printf("\texecuting TestID: %i...\n", iTestSelectionID);

        switch (iTestSelectionID)
        {
            case 1:
            {
                iHparams[0] = G_iUSBPortNumber;
                iHparams[1] = G_iBaudRate;
                iHparams[2] = G_iParity;
                iHparams[3] = 1; // Block
                iHparams[4] = 1; // Ignore Newlines;
                
                printf("Please enter the command: \n");
                fgets(csCommand, sizeof(csCommand), stdin);

                // Null terminate and remove new line character
                csCommand[strlen(csCommand)-1] = '\0';

                // Add on optional terminator
                switch(G_iTerminationOption)
                {

                    case 0:
                    {
                        // Add nothing
                        break;
                    }
                    
                    case 1:
                    {
                        strcat(csCommand, "\r");
                        break;
                    }

                    case 2:
                    {
                        strcat(csCommand, "\n\r");
                        break;
                    }

                    default:
                    {
                        printf("Invalid block flag value entered. Defaulting to 1.\n");
                        strcat(csCommand, "\r");
                    } 

                } // end switch

                
                iWriteLength = strlen(csCommand);
                
                iReadLength = MAXLENGTH;
                iWaitTime = 2000;
                
                iReturn = ATLAS_Native_Generic_Serial(csReadBuffer, csCommand,
                                                      iHparams, iReadLength,
                                                      iWriteLength, iWaitTime,
                                                      &iNumBytesRead);
                if (SUCCESS == iReturn)
                {
                    printf("ATLAS_Native_Generic_Serial test successful\n");
                    printf("\t Read buffer = %s\n\n", csReadBuffer);
                }
                else
                {
                    printf("Error in ATLAS_Native_Generic_Serial\n");
                }
                break;
            }

            case 98:
            {
                // Prompt for and set USB port to write to
                printf("Please enter the USB port number: \n");
                fgets(G_csUSBPortNumber, sizeof(G_csUSBPortNumber), stdin);
                // Convert the USB port number to an integer.
                G_iUSBPortNumber = atoi(G_csUSBPortNumber);
                
                printf("Port Number Successfully Set!\n");
                
                // Prompt for and set baud rate
                //printf("Please enter the baud rate you would like to set: \n");
                //fgets(G_csBaudRate, sizeof(G_csBaudRate), stdin);
                // Convert the baud rate entered to an integer. 
                G_iBaudRate = 57600;

                // Prompt for and set parity
                //printf("Please enter if parity is off or on (0=off, 1=on): \n");
                //fgets(G_csParity, sizeof(G_csParity), stdin);
                G_iParity = 0;
                if (G_iParity != 0 && G_iParity != 1)
                {
                    printf("Invalid parity value entered. Defaulting to 0 (none).\n");
                    G_iParity = 0;
                }

                // Prompt for and set blocking flag
                //printf("Line feed options:\n\t0 - No Line Feed \n\t1 - LF only\n\t2 - Newline\n");
                //fgets(G_csTerminationOption, sizeof(G_csTerminationOption), stdin);
                G_iTerminationOption = 2;
       
                // Port Number set, don't need to prompt user to set again.
                iNeedToSetFlag = 1;
                
                break;
            }
            
            case 99:
            {
                // Do nothing, let the loop exit
                break;
            }
            
            default:
            {
                printf("ERROR - Test ID %i does not exist!\n\n", iTestSelectionID);
                break;
            }
        }
    }// end while

    printf("\n\nATLAS_Native_Serial_Handler Test Console end.\n");
    
    return SUCCESS;
}
