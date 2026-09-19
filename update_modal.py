import re

with open('backend/templates/admin/customer_360.html', 'r', encoding='utf-8') as f:
    content = f.read()

# We need to replace the editModal div with the new tabbed version.
# First, let's locate the start of editModal
start_idx = content.find('<div id="editModal"')
end_idx = content.find('</div>\n</div>\n\n<script>', start_idx)

if start_idx != -1 and end_idx != -1:
    end_idx += 13 # include '</div>\n</div>'
    
    new_modal = """<div id="editModal" class="fixed inset-0 bg-black/50 z-50 hidden items-center justify-center p-4">
    <div class="bg-white rounded-xl shadow-xl w-full max-w-5xl max-h-[90vh] flex flex-col">
        <!-- Header -->
        <div class="flex justify-between items-center p-4 border-b border-gray-100">
            <div>
                <h3 class="text-lg font-bold text-gray-800">Hồ sơ khách hàng</h3>
                <p class="text-sm text-gray-500" id="modal-subtitle">Thông tin cá nhân</p>
            </div>
            
            <div class="flex items-center gap-4">
                <div class="flex bg-gray-100 p-1 rounded-lg">
                    <button type="button" onclick="switchModalTab('general')" id="btn-modal-general" class="modal-tab-btn px-4 py-1.5 text-sm font-semibold bg-white text-blue-600 shadow-sm rounded-md transition-all">Thông tin chung</button>
                    <button type="button" onclick="switchModalTab('other')" id="btn-modal-other" class="modal-tab-btn px-4 py-1.5 text-sm font-semibold text-gray-500 hover:text-gray-700 rounded-md transition-all">Khác</button>
                </div>
                <button type="button" onclick="document.getElementById('editModal').style.display='none'" class="text-gray-400 hover:text-gray-600 text-2xl font-bold leading-none">&times;</button>
            </div>
        </div>
        
        <!-- Body -->
        <div class="overflow-y-auto p-4">
            <form method="POST" action="" class="space-y-4" id="editCustomerForm">
                {% csrf_token %}
                <input type="hidden" name="action" value="update_info">
                
                <!-- TAB THÔNG TIN CHUNG -->
                <div id="modal-tab-general" class="modal-tab-content block">
                    <!-- Khối 1: Thông tin cá nhân -->
                    <fieldset class="border border-gray-200 rounded-lg p-4 bg-gray-50/50 mb-4">
                        <div class="flex justify-between items-center mb-4">
                            <legend class="text-sm font-bold text-gray-700 px-2">Thông tin cá nhân</legend>
                            <div class="flex gap-4 text-sm items-center">
                                <label class="flex items-center gap-1 cursor-pointer"><input type="radio" name="gender" value="Nam" {% if customer.gender == 'Nam' %}checked{% endif %} class="text-blue-600"> Nam</label>
                                <label class="flex items-center gap-1 cursor-pointer"><input type="radio" name="gender" value="Nữ" {% if customer.gender == 'Nữ' %}checked{% endif %} class="text-blue-600"> Nữ</label>
                                <label class="flex items-center gap-1 cursor-pointer ml-4"><input type="checkbox" name="create_appointment" class="rounded text-blue-600"> Tạo lịch hẹn</label>
                            </div>
                        </div>

                        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                            <!-- Avatar area (placeholder) -->
                            <div class="col-span-1 flex flex-col items-center justify-start pt-2">
                                <div class="w-24 h-24 bg-gray-200 rounded-lg mb-2"></div>
                                <a href="#" class="text-xs text-blue-500 flex items-center gap-1"><span class="border rounded-full w-4 h-4 inline-flex items-center justify-center text-[10px]">i</span> Hướng dẫn</a>
                            </div>

                            <div class="col-span-3 grid grid-cols-1 md:grid-cols-3 gap-4">
                                <div>
                                    <label class="block text-xs font-semibold text-gray-700 mb-1">Họ và tên *</label>
                                    <input type="text" name="name" value="{{ customer.name }}" required class="w-full border border-gray-300 rounded-md p-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                                </div>
                                <div>
                                    <label class="block text-xs font-semibold text-gray-700 mb-1">Ngày sinh</label>
                                    <input type="date" name="customer_dob" value="{{ customer.customer_dob|date:'Y-m-d' }}" class="w-full border border-gray-300 rounded-md p-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                                </div>
                                <div>
                                    <label class="block text-xs font-semibold text-gray-700 mb-1">Số điện thoại *</label>
                                    <input type="text" name="phone" value="{{ customer.phone }}" required class="w-full border border-gray-300 rounded-md p-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                                </div>
                                
                                <div>
                                    <label class="block text-xs font-semibold text-gray-700 mb-1">Chi nhánh</label>
                                    <select name="branch" class="w-full border border-gray-300 rounded-md p-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                                        <option value="">-- Chọn Chi nhánh --</option>
                                    </select>
                                </div>
                                <div>
                                    <label class="block text-xs font-semibold text-gray-700 mb-1 text-green-600">Nhóm khách hàng</label>
                                    <select name="customer_type" class="w-full border border-gray-300 rounded-md p-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                                        <option value="Mới" {% if customer.customer_type == 'Mới' %}selected{% endif %}>Khách Mới</option>
                                        <option value="Cũ" {% if customer.customer_type == 'Cũ' %}selected{% endif %}>Khách Cũ</option>
                                    </select>
                                </div>
                                <div>
                                    <label class="block text-xs font-semibold text-gray-700 mb-1">Email</label>
                                    <input type="email" name="email" value="{{ customer.email|default:'' }}" class="w-full border border-gray-300 rounded-md p-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                                </div>

                                <div>
                                    <label class="block text-xs font-semibold text-gray-700 mb-1 text-green-600">Nguồn khách hàng</label>
                                    <select name="customer_source" class="w-full border border-gray-300 rounded-md p-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                                        <option value="">-- Chọn Nguồn --</option>
                                        <option value="Facebook" {% if customer.customer_source == 'Facebook' %}selected{% endif %}>Facebook</option>
                                        <option value="Zalo" {% if customer.customer_source == 'Zalo' %}selected{% endif %}>Zalo</option>
                                        <option value="Khách Vãng Lai" {% if customer.customer_source == 'Khách Vãng Lai' %}selected{% endif %}>Khách Vãng Lai</option>
                                    </select>
                                </div>
                                <div>
                                    <label class="block text-xs font-semibold text-gray-700 mb-1 text-green-600">Nguồn chi tiết</label>
                                    <input type="text" name="source_detail" value="{{ customer.source_detail|default:'' }}" class="w-full border border-gray-300 rounded-md p-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                                </div>
                                <div>
                                    <label class="block text-xs font-semibold text-gray-700 mb-1">Quốc tịch</label>
                                    <input type="text" name="nationality" value="{{ customer.nationality|default:'Vietnam' }}" class="w-full border border-gray-300 rounded-md p-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                                </div>
                                
                                <div>
                                    <label class="block text-xs font-semibold text-gray-700 mb-1">Nghề nghiệp</label>
                                    <input type="text" name="profession" value="{{ customer.profession|default:'' }}" class="w-full border border-gray-300 rounded-md p-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                                </div>
                                
                                <div class="col-span-3 grid grid-cols-1 md:grid-cols-3 gap-4">
                                    <div>
                                        <label class="block text-xs font-semibold text-gray-700 mb-1">Địa chỉ</label>
                                        <input type="text" name="address" value="{{ customer.address|default:'' }}" class="w-full border border-gray-300 rounded-md p-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                                    </div>
                                    <div>
                                        <label class="block text-xs font-semibold text-gray-700 mb-1">Tỉnh/Thành phố</label>
                                        <input type="text" name="city" value="{{ customer.city|default:'' }}" class="w-full border border-gray-300 rounded-md p-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                                    </div>
                                    <div>
                                        <label class="block text-xs font-semibold text-gray-700 mb-1">Phường xã</label>
                                        <input type="text" name="district" value="{{ customer.district|default:'' }}" class="w-full border border-gray-300 rounded-md p-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                                    </div>
                                </div>

                                <div>
                                    <label class="block text-xs font-semibold text-gray-700 mb-1">Khách cũ</label>
                                    <div class="flex items-center gap-2 border border-gray-300 rounded-md p-2 bg-white">
                                        <input type="checkbox" name="is_old_customer" {% if customer.old_customer_code %}checked{% endif %} class="rounded">
                                        <input type="text" name="old_customer_code" value="{{ customer.old_customer_code|default:'' }}" placeholder="eg. mã khách hàng cũ" class="w-full outline-none text-sm">
                                    </div>
                                </div>
                                <div>
                                    <label class="block text-xs font-semibold text-gray-700 mb-1">Ngôn ngữ</label>
                                    <input type="text" name="language" value="{{ customer.language|default:'' }}" class="w-full border border-gray-300 rounded-md p-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                                </div>
                                <div>
                                    <label class="block text-xs font-semibold text-gray-700 mb-1">Chi nhánh dự kiến</label>
                                    <input type="text" name="expected_clinic" value="{{ customer.expected_clinic|default:'' }}" class="w-full border border-gray-300 rounded-md p-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                                </div>
                                
                                <div class="col-span-3">
                                    <label class="block text-xs font-semibold text-gray-700 mb-1">Ghi chú</label>
                                    <textarea name="general_note" rows="2" class="w-full border border-gray-300 rounded-md p-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none">{{ customer.general_note|default:'' }}</textarea>
                                </div>
                            </div>
                        </div>
                    </fieldset>

                    <!-- Khối 2: CMND/CC -->
                    <fieldset class="border border-gray-200 rounded-lg p-4 bg-gray-50/50 mb-4">
                        <legend class="text-sm font-bold text-gray-700 px-2">CMND/CCCD</legend>
                        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div>
                                <label class="block text-xs font-semibold text-gray-700 mb-1">Số CMND/CCCD</label>
                                <input type="text" name="identity_card" value="{{ customer.identity_card|default:'' }}" class="w-full border border-gray-300 rounded-md p-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                            </div>
                            <div>
                                <label class="block text-xs font-semibold text-gray-700 mb-1">Ngày cấp</label>
                                <input type="date" name="id_issue_date" value="{{ customer.id_issue_date|date:'Y-m-d' }}" class="w-full border border-gray-300 rounded-md p-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                            </div>
                            <div>
                                <label class="block text-xs font-semibold text-gray-700 mb-1">Nơi cấp</label>
                                <input type="text" name="id_issue_place" value="{{ customer.id_issue_place|default:'' }}" class="w-full border border-gray-300 rounded-md p-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                            </div>
                        </div>
                    </fieldset>

                    <!-- Khối 3: Bảo hiểm -->
                    <fieldset class="border border-gray-200 rounded-lg p-4 bg-gray-50/50">
                        <legend class="text-sm font-bold text-gray-700 px-2">Bảo hiểm</legend>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label class="block text-xs font-semibold text-gray-700 mb-1">Đối tượng bảo hiểm</label>
                                <select name="insurance_type" class="w-full border border-gray-300 rounded-md p-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                                    <option value="">-- Chọn đối tượng --</option>
                                    <option value="Thu phí" {% if customer.insurance_type == 'Thu phí' %}selected{% endif %}>Thu phí</option>
                                    <option value="Miễn phí" {% if customer.insurance_type == 'Miễn phí' %}selected{% endif %}>Miễn phí</option>
                                </select>
                            </div>
                            <div>
                                <label class="block text-xs font-semibold text-gray-700 mb-1">Mã bảo hiểm</label>
                                <input type="text" name="insurance_code" value="{{ customer.insurance_code|default:'' }}" class="w-full border border-gray-300 rounded-md p-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                            </div>
                        </div>
                    </fieldset>
                </div>

                <!-- TAB KHÁC -->
                <div id="modal-tab-other" class="modal-tab-content hidden">
                    <fieldset class="border border-gray-200 rounded-lg p-4 bg-gray-50/50">
                        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                            <div>
                                <label class="block text-xs font-semibold text-gray-700 mb-1">Facebook</label>
                                <input type="text" name="facebook_link" value="{{ customer.facebook_link|default:'' }}" placeholder="Facebook.com/" class="w-full border border-gray-300 rounded-md p-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                            </div>
                            <div>
                                <label class="block text-xs font-semibold text-gray-700 mb-1">Zalo</label>
                                <input type="text" name="zalo_link" value="{{ customer.zalo_link|default:'' }}" placeholder="Zalo.me/" class="w-full border border-gray-300 rounded-md p-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                            </div>
                            <div>
                                <label class="block text-xs font-semibold text-gray-700 mb-1">Viber</label>
                                <input type="text" name="viber_link" value="{{ customer.viber_link|default:'' }}" placeholder="Viber.com/" class="w-full border border-gray-300 rounded-md p-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                            </div>
                            <div>
                                <label class="block text-xs font-semibold text-gray-700 mb-1">Instagram</label>
                                <input type="text" name="instagram_link" value="{{ customer.instagram_link|default:'' }}" placeholder="Instagram.com/" class="w-full border border-gray-300 rounded-md p-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                            </div>
                            <div class="col-span-4">
                                <label class="block text-xs font-semibold text-gray-700 mb-1">GDrive</label>
                                <input type="text" name="gdrive_link" value="{{ customer.gdrive_link|default:'' }}" class="w-full border border-gray-300 rounded-md p-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                            </div>
                            <div>
                                <label class="block text-xs font-semibold text-gray-700 mb-1">Số điện thoại 2 (10 ký tự số)</label>
                                <input type="text" name="phone_2" value="{{ customer.phone_2|default:'' }}" placeholder="eg. số điện thoại" class="w-full border border-gray-300 rounded-md p-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                            </div>
                            <div>
                                <label class="block text-xs font-semibold text-gray-700 mb-1">Hộ chiếu</label>
                                <input type="text" name="passport" value="{{ customer.passport|default:'' }}" placeholder="eg. hộ chiếu" class="w-full border border-gray-300 rounded-md p-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                            </div>
                            <div>
                                <label class="block text-xs font-semibold text-gray-700 mb-1">Dân tộc</label>
                                <input type="text" name="ethnicity" value="{{ customer.ethnicity|default:'' }}" placeholder="eg. dân tộc" class="w-full border border-gray-300 rounded-md p-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                            </div>
                            <div>
                                <label class="block text-xs font-semibold text-gray-700 mb-1">Tôn giáo</label>
                                <select name="religion" class="w-full border border-gray-300 rounded-md p-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                                    <option value="">tôn giáo</option>
                                    <option value="Không" {% if customer.religion == 'Không' %}selected{% endif %}>Không</option>
                                    <option value="Phật giáo" {% if customer.religion == 'Phật giáo' %}selected{% endif %}>Phật giáo</option>
                                    <option value="Thiên chúa giáo" {% if customer.religion == 'Thiên chúa giáo' %}selected{% endif %}>Thiên chúa giáo</option>
                                </select>
                            </div>
                            <div>
                                <label class="block text-xs font-semibold text-gray-700 mb-1">Nhân viên marketing</label>
                                <input type="text" name="marketing_staff" value="{{ customer.marketing_staff|default:'' }}" placeholder="nhân viên marketing" class="w-full border border-gray-300 rounded-md p-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                            </div>
                            <div>
                                <label class="block text-xs font-semibold text-gray-700 mb-1">Gclid</label>
                                <input type="text" name="gclid" value="{{ customer.gclid|default:'' }}" placeholder="eg. gclid" class="w-full border border-gray-300 rounded-md p-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                            </div>
                            <div>
                                <label class="block text-xs font-semibold text-gray-700 mb-1">ĐVQHNS</label>
                                <input type="text" name="dvqhns" value="{{ customer.dvqhns|default:'' }}" placeholder="eg. đvqhns" class="w-full border border-gray-300 rounded-md p-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                            </div>
                            <div class="col-span-4 mt-2">
                                <label class="block text-xs font-semibold text-gray-700 mb-1">Ghi chú</label>
                                <textarea name="medical_notes" rows="3" placeholder="eg. ghi chú" class="w-full border border-gray-300 rounded-md p-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none">{{ customer.medical_notes|default:'' }}</textarea>
                            </div>
                        </div>
                    </fieldset>
                </div>
                
                <!-- Footer -->
                <div class="flex justify-end gap-3 pt-4 mt-4 bg-white sticky bottom-0">
                    <button type="button" onclick="document.getElementById('editModal').style.display='none'" class="px-5 py-2 bg-gray-400 text-white font-bold rounded-md hover:bg-gray-500 transition">Đóng</button>
                    <button type="submit" class="bg-blue-600 text-white px-5 py-2 rounded-md font-bold shadow hover:bg-blue-700 transition">Lưu</button>
                </div>
            </form>
        </div>
    </div>
</div>

<script>
    function switchModalTab(tabId) {
        document.querySelectorAll('.modal-tab-content').forEach(el => {
            el.classList.remove('block');
            el.classList.add('hidden');
        });
        
        document.getElementById('modal-tab-' + tabId).classList.remove('hidden');
        document.getElementById('modal-tab-' + tabId).classList.add('block');
        
        const btnGeneral = document.getElementById('btn-modal-general');
        const btnOther = document.getElementById('btn-modal-other');
        
        if (tabId === 'general') {
            btnGeneral.className = "modal-tab-btn px-4 py-1.5 text-sm font-semibold bg-white text-blue-600 shadow-sm rounded-md transition-all";
            btnOther.className = "modal-tab-btn px-4 py-1.5 text-sm font-semibold text-gray-500 hover:text-gray-700 rounded-md transition-all";
            document.getElementById('modal-subtitle').innerText = "Thông tin cá nhân";
        } else {
            btnOther.className = "modal-tab-btn px-4 py-1.5 text-sm font-semibold bg-white text-blue-600 shadow-sm rounded-md transition-all";
            btnGeneral.className = "modal-tab-btn px-4 py-1.5 text-sm font-semibold text-gray-500 hover:text-gray-700 rounded-md transition-all";
            document.getElementById('modal-subtitle').innerText = "Thông tin khác";
        }
    }
</script>
"""

    content = content[:start_idx] + new_modal + content[end_idx:]
    with open('backend/templates/admin/customer_360.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated editModal successfully!")
else:
    print("Could not find editModal block")

