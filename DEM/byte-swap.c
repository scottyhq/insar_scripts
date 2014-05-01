
/* compile cc -o byte-swap byte-swap.c
 *    written by: Brian Savage
 *       savage13@gps.caltech.edu
 *          March 25, 2003
 *
 *             byte-swap will byte swap a flat binary file
 *                of any length and any number length
 *
 *                */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>

/*
 *   void swap(char *p, int len)
 *
 *     *p is a pointer to an memory space
 *       and points to the first byte of our "thing"
 *         len is the length of our "thing" we want to swap
 *           
 *             our number is represented by [0][1][2][3]...
 *               Where each [#] represents a byte
 *
 *                 For 4 bytes 
 *                   byte swapping means taking
 *                     [0][1][2][3] and turning it into
 *                       [3][2][1][0]
 *
 *                         2 bytes
 *                           [0][1] => [1][0]
 *
 *                           */

void
swap(char *p, int len) {
		  int i;
		    char tmp;
			  for(i = 0; i < len/2; i++) {
					      tmp = p[len-i-1];
						      p[len-i-1] = p[i];
							      p[i] = tmp;
								    }
}

int
main(int argc, char *argv[]) {
		  void *in;
		    int len;

			  if(argc < 2) {
					      fprintf(stderr, "usage %s [size in bytes] < in > out\n", argv[0]);
						      exit(-1);
							    }
			    
			    fprintf(stderr, "Reading from stdin and writing swapped output to stdout\n");
				  len = atoi(argv[1]);
				    in = (void *) malloc(len);
					  /* Read in the data */
					  while(fread(in, len, 1, stdin) == 1) {
							      /* Byte swap the data */
							      swap((char*)in,len);
								      /* Rewrite back into the file */
								      fwrite(in, len, 1, stdout);
									    }
					    free(in);
						  return(0);
}

