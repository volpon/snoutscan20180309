package com.provisionlab.snoutscan.adapters;

import android.content.Context;
import android.support.v4.app.Fragment;
import android.support.v4.app.FragmentManager;
import android.support.v4.app.FragmentPagerAdapter;

import com.provisionlab.snoutscan.R;
import com.provisionlab.snoutscan.fragments.TutorialItemFragment;

/**
 * Created by Evgeniy on 21-Jan-18.
 */

public class TutorialPagerAdapter extends FragmentPagerAdapter {

    private static final int ITEMS_NUMBER = 3;
    private Context context;

    public TutorialPagerAdapter(Context context, FragmentManager fm) {
        super(fm);
        this.context = context;
    }

    @Override
    public Fragment getItem(int position) {

        switch (position) {
            case 0:
                return TutorialItemFragment.newInstance(R.drawable.tutorial_image_1, context.getString(R.string.tutorial_text_1));
            case 1:
                return TutorialItemFragment.newInstance(R.drawable.tutorial_image_2, context.getString(R.string.tutorial_text_2));
            case 2:
                return TutorialItemFragment.newInstance(R.drawable.tutorial_image_3, context.getString(R.string.tutorial_text_3));
            default:
                return null;
        }
    }

    @Override
    public int getCount() {
        return ITEMS_NUMBER;
    }
}
