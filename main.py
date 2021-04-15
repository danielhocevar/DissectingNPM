"""
This file uses the subprocess library to initialize the website.
It also contains code to preview how we generate our data.

-----------------------------------------
INSTRUCTIONS: Previewing data generation!
------------------------------------------
You can test our data creator by commenting out line 48.
Note that you will need a stable internet connection for this to work.

Please refer to the in-line comments for more details.


Copyright and Usage Information
===============================
This file is Copyright (c) 2021 Daniel Hocevar and Roman Zupancic. 

This files contents may not be modified or redistributed without written
permission from Daniel Hocevar and Roman Zupancic
"""

import subprocess
import assemble_data

def main() -> None:
    """
    Call < streamlit run site_main.py > to start the streamlit website.
    """
    subprocess.run(['streamlit', 'run', 'site_main.py'])


if __name__ == '__main__':
    # To test the efficacy of our data generation algorithms,
    # uncomment line after this section.
    # 
    # You should see a semi-steady stream of printouts signaling the current package
    # the algorithm is processing, and the amount of packages (including dependencies)
    # its seen so far.
    # 
    # If you'd like to see it generate more packages, raise the value of the second parameter.
    #
    # Upon completion of the generation, you should see a file 'test_packages.csv' in the
    # project root. This file should have the same few first lines as 'big_v2.csv', and
    # is in the same format.
    #
    # UNCOMMENT THIS LINE:
    # --------------------
    assemble_data.get_detailed_data('popular.txt', 10, 'test_packages.csv')

    # This line runs the main program.
    # If you'd like, you can comment this line while you run the data generation.
    # main()
