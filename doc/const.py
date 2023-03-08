AllPanels = {
    'admin_panels': {
        'persian_name': 'پنل ادمین',
        'sub_panels': {
            # 'admin_waiting_user': 'تایید کاربران',
            # 'admin_accepted_user': 'کاربران تایید شده',
            'admin_upload': 'آپلود فایل',
            # 'admin_user_recommendation': 'مشاهده نظرات کاربران',
            'admin_user_report_bug': 'مشاهده گزارشات خطاها',
            'admin_accept_user_comments': 'نظرات تحلیل اسناد',
            'super_admin_user_log': 'لاگ کاربران'
        }
    },

    'information': {
        'persian_name': 'پروفایل اخبار',
        'sub_panels': {
            'information': 'پروفایل اخبار',
        }
    },
    
    'search': {
        'persian_name': 'جستجوی پیشرفته',
        'sub_panels': {
            'search': 'جستجوی پیشرفته',
        }
    },
    
    'AI_analysis': {
        'persian_name': 'تحلیل هوشمند',
        'sub_panels': {
            'AI_topics': 'دسته‌بندی موضوعی (LDA)',
            'paragraph_clustering': 'خوشه بندی پاراگراف‌ها',
            'ManualClustering': 'خوشه بندی سفارشی',
            'knowledgeGraph': 'گراف دانش',
        }
    },
    
    'resource_profile': {
        'persian_name': 'پروفایل منابع',
        'sub_panels': {
            'resource_profile_tab': 'پروفایل منابع',
        }
    },
}

OtherPanels = {

}

ALLPANELS = {**AllPanels, **OtherPanels}
