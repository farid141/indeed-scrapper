from jobseeking.jobseeking import Jobseeking
from jobseeking import constants as const
import pandas as pd


next_page = 1
job_df = pd.DataFrame()

job_inst = Jobseeking()
job_inst.land_first_page()
while next_page:
    # close subscription offer
    job_inst.close_email_subs()

    # extract all jobs on page
    new_df = job_inst.extract_jobs_page()

    if job_df.empty:
        job_df = new_df
    else:
        job_df = pd.concat(
            [job_df, new_df],
            axis=0,
            ignore_index=True
        )

    # check pagination and click next
    next_page = job_inst.check_pagination()


job_df.to_csv(const.FILE_OUT, index=False)
